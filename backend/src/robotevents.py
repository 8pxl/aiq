import logging
import time
from typing import Any, Optional
import requests
from enum import Enum
from sqlmodel import Session, select
import db
from tables import Qualification, Qualifications, Teams
from progress_tracker import ProgressTracker


class RobotEvents:
    token: str
    header: dict[str, str]
    base: str
    season: int
    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(self, token: str):
        self.token = token
        self.base = "https://www.robotevents.com/api/v2"
        self.season = 197
        # self.season = 190
        self.header = {"Authorization": f"Bearer {token}"}

    def request(self, path: str, max_retries=5, delay=17) -> Any | None:  # pyright: ignore[reportExplicitAny]
        if not path.startswith("/"):
            self.logger.exception("path needs to start with a blackslash")
            return None
        url = self.base + path
        for attempt in range(max_retries):
            res = requests.get(url, headers=self.header)
            try:
                res.raise_for_status()
                return res.json()  # pyright: ignore[reportAny]
            except requests.RequestException as exc:
                self.logger.exception("API request failed: %s %s", url, exc)
                if attempt < max_retries - 1:
                    print(f"failed retry {attempt}, waiting, {delay} seconds")
                    time.sleep(delay)
        return None

    def get_qualifications(self, robotevents_id: int) -> Qualification:
        awards = self.request(
            f"/teams/{str(robotevents_id)}/awards?season%5B%5D={self.season}"
        )
        if not awards:
            return Qualification.NONE
        awards = awards["data"]
        highest = Qualification.NONE
        for award in awards:
            # print(award)
            if award["qualifications"]:
                for qual in award["qualifications"]:
                    new = Qualification.from_string(qual)
                    if new.value > highest.value:
                        highest = new
        return highest

    # def create_team(self, robotevents_id: int,res: any, rank: int, score:int, programming: int, driver: int): res = self.request(f"/teams/{robotevents_id}")
    #     if not res:
    #         return None
    #
    #     country: str = res['location']['country'],  # pyright: ignore[reportAny, reportAssignmentType]
    #     region: str| None = res['location']['region']
    #     if not region:
    #         region = country
    #     print("creaing team", id)
    #     team = Teams(
    #         id = res['id'],  # pyright: ignore[reportAny]
    #         number = res['number'],  # pyright: ignore[reportAny]
    #         organization = res['organization'],   # pyright: ignore[reportAny]
    #         country = country,
    #         region = region,
    #         registered = res['registered'],  # pyright: ignore[reportAny]
    #         grade = res['grade'],  # pyright: ignore[reportAny]
    #         qualification = self.get_qualifications(res['id']),  # pyright: ignore[reportAny]
    #         world_rank = rank,
    #         score = score,
    #         programming = programming,
    #         driver = driver
    #     )
    #     return team
    #
    def parse_skills(self, session, ms: bool):
        """
        Parse skills rankings and update/create teams in the database.

        For existing teams: updates world_rank, score, programming, and driver fields
        For new teams: creates full team record with all fields

        Args:
            session: SQLModel Session object for database operations
            ms: Boolean - True for Middle School, False for High School
        """
        if ms:
            url = f"https://www.robotevents.com/api/seasons/{self.season}/skills?post_season=0&grade_level=Middle%20School"
        else:
            url = f"https://www.robotevents.com/api/seasons/{self.season}/skills?post_season=0&grade_level=High%20School"

        res = requests.get(url)
        try:
            res.raise_for_status()
        except requests.RequestException as exc:
            self.logger.exception("API request failed: %s %s", url, exc)
            return

        res = res.json()
        updated_count = 0
        created_count = 0
        start = time.time()

        for team_data in res:
            print(
                f"Processing team {team_data['team']['team']} (took {time.time() - start:.2f}s)"
            )
            start = time.time()

            tt = team_data["team"]
            team_id = tt["id"]  # pyright: ignore[reportAny]

            # Check if team already exists in database
            existing_team = session.get(Teams, team_id)

            if existing_team:
                # Update existing team's skill scores
                existing_team.world_rank = team_data["rank"]
                existing_team.score = team_data["scores"]["score"]
                existing_team.programming = team_data["scores"]["programming"]
                existing_team.driver = team_data["scores"]["driver"]
                updated_count += 1
                print(f"  Updated existing team: {existing_team.number}")
            else:
                # Create new team with all fields
                country: str = tt["country"]  # pyright: ignore[reportAny, reportAssignmentType]
                region: str | None = tt["eventRegion"]
                if not region:
                    region = country

                new_team = Teams(
                    id=team_id,
                    number=tt["team"],  # pyright: ignore[reportAny]
                    organization=tt["organization"],  # pyright: ignore[reportAny]
                    country=country,
                    region=region,
                    grade=tt["gradeLevel"],  # pyright: ignore[reportAny]
                    world_rank=team_data["rank"],
                    score=team_data["scores"]["score"],
                    programming=team_data["scores"]["programming"],
                    driver=team_data["scores"]["driver"],
                )
                session.add(new_team)
                created_count += 1
                print(f"  Created new team: {new_team.number}")

            # Commit every 100 teams to avoid keeping too much in memory
            if (updated_count + created_count) % 100 == 0:
                session.commit()
                print(f"  Progress: {updated_count} updated, {created_count} created")

            if (updated_count + created_count) >= 10000:
                print("10000 team limit reached!")
                break

        # Final commit for remaining teams
        session.commit()
        print(
            f"\nCompleted: {updated_count} teams updated, {created_count} teams created"
        )
        return updated_count, created_count

    def get_worlds_teams(self) -> list[int] | None:
        event = "/events/58909/teams"

        res = self.request(event)
        if not res:
            return None
        pages = res["meta"]["last_page"]
        print(pages)
        teams = []
        for i in range(1, pages + 1):
            if i >= 2:
                break
            res = self.request(event + f"?page={i}")
            if not res:
                continue
            res = res["data"]
            page = 1
            print(len(res))
            for team in res:
                teams.append(team["id"])
        return teams

    def create_qualifications_full(
        self,
        session: Session,
        teams: list[int],
        resume: bool = True,
        progress_tracker: Optional[ProgressTracker] = None,
        commit_interval: int = 10,
    ):
        """
        Create qualifications for all teams with progress tracking and resumption support.
        Periodically commits to database to prevent data loss on interruption.

        Args:
            session: SQLModel Session object for database operations
            teams: List of team IDs to process
            resume: Whether to resume from last checkpoint (default: True)
            progress_tracker: Optional ProgressTracker instance (creates new one if None)
            commit_interval: How often to commit to database (default: every 10 teams)

        Returns:
            Number of qualifications processed
        """
        # Initialize progress tracker
        if progress_tracker is None:
            progress_tracker = ProgressTracker()

        start_index = progress_tracker.initialize(len(teams), resume=resume)

        # worlds_teams = self.get_worlds_teams()
        worlds_teams = None
        processed_count = 0

        try:
            for i in range(start_index, len(teams)):
                team = teams[i]

                # Determine qualification status
                if worlds_teams and team in worlds_teams:
                    q = Qualification.WORLD
                else:
                    q = self.get_qualifications(team)

                # Upsert to database immediately
                qual_obj = Qualifications(team_id=team, status=q)
                db.upsert_quals(session, qual_obj)
                processed_count += 1

                # Update progress tracker
                progress_tracker.update_progress(i, team, q.name)

                # Periodic commit to save progress to database
                if processed_count % commit_interval == 0:
                    session.commit()
                    progress_tracker._log(
                        f"Database committed at {processed_count} teams"
                    )

            # Final commit for any remaining changes
            session.commit()

            # Mark as complete
            progress_tracker.complete()

        except KeyboardInterrupt:
            session.commit()  # Save progress before exiting
            progress_tracker._log(
                "INTERRUPTED: Progress committed to database. Run again to resume."
            )
            raise
        except Exception as e:
            session.commit()  # Try to save progress even on error
            progress_tracker._log(
                f"ERROR: {e}. Progress committed to database. Run again to resume."
            )
            raise

        return processed_count

    def create_qualifications_worlds(
        self, teams: list[int]
    ) -> list[Qualifications] | None:
        worlds_teams = self.get_worlds_teams()
        if not worlds_teams:
            return None
        return [
            Qualifications(team_id=id, status=Qualification.WORLD)
            for id in worlds_teams
        ]

    def award_contains(self, award: str, strings: list[str]) -> bool:
        for s in strings:
            if s in award:
                return True
        return False

    def create_qualifications_sig(self) -> list[Qualifications] | None:
        res = self.request(
            f"/events?season%5B%5D={self.season}&level%5B%5D=Signature&myEvents=false"
        )
        if not res:
            return None
        ids: list[int] = []
        sig_quals = ["Excellence", "Tournament Champions"]
        qualified: list[Qualifications] = []
        for event in res["data"]:
            if event["awards_finalized"]:
                ids.append(event["id"])
        count = 0
        for id in ids[14:]:
            print("checking sig: ", id)
            res = self.request(f"/events/{id}/awards")
            if not res:
                self.logger.exception("failed GET on event id ", id)
                continue
            for award in res["data"]:
                if self.award_contains(award["title"], sig_quals):
                    for winner in award["teamWinners"]:
                        qualified.append(
                            Qualifications(
                                team_id=winner["team"]["id"], status=Qualification.WORLD
                            )
                        )
        return qualified
