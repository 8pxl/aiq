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
    progress_tracker: Optional[ProgressTracker] = None

    def __init__(self, token: str, progress_tracker: Optional[ProgressTracker] = None):
        self.token = token
        self.base = "https://www.robotevents.com/api/v2"
        self.season = 197
        # self.season = 190
        self.header = {"Authorization": f"Bearer {token}"}
        self.progress_tracker = progress_tracker

    def request(
        self,
        path: str,
        max_retries=5,
        base_delay=2,
        max_delay=60,
    ) -> Any | None:  # pyright: ignore[reportExplicitAny]
        """
        Make an API request with exponential backoff retry logic.

        Args:
            path: API endpoint path (must start with /)
            max_retries: Maximum number of retry attempts (default: 5)
            base_delay: Initial delay in seconds for exponential backoff (default: 2)
            max_delay: Maximum delay in seconds (default: 60)

        Returns:
            JSON response data or None on failure
        """
        if not path.startswith("/"):
            error_msg = f"ERROR: path needs to start with a forward slash: {path}"
            self.logger.error(error_msg)
            if self.progress_tracker:
                self.progress_tracker._log(error_msg)
            return None
        url = self.base + path

        for attempt in range(max_retries):
            try:
                res = requests.get(url, headers=self.header)
                res.raise_for_status()
                # Log successful request on first attempt or after retry
                if attempt > 0:
                    success_msg = (
                        f"✓ SUCCESS: Request succeeded on attempt {attempt + 1}: {path}"
                    )
                    self.logger.info(success_msg)
                    if self.progress_tracker:
                        self.progress_tracker._log(success_msg)
                return res.json()  # pyright: ignore[reportAny]

            except requests.HTTPError as exc:
                status_code = exc.response.status_code if exc.response else "unknown"
                error_msg = f"✗ HTTP ERROR [{status_code}]: {path} (attempt {attempt + 1}/{max_retries})"
                self.logger.error(error_msg)
                if self.progress_tracker:
                    self.progress_tracker._log(error_msg)

                if attempt < max_retries - 1:
                    # Exponential backoff: 2, 4, 8, 16, 32, ... (capped at max_delay)
                    delay = min(base_delay * (2**attempt), max_delay)
                    retry_msg = (
                        f"  ⟳ RETRYING in {delay:.1f} seconds (exponential backoff)..."
                    )
                    self.logger.warning(retry_msg)
                    if self.progress_tracker:
                        self.progress_tracker._log(retry_msg)
                    time.sleep(delay)
                else:
                    final_msg = f"✗ FAILED: Max retries reached for {path}"
                    self.logger.error(final_msg)
                    if self.progress_tracker:
                        self.progress_tracker._log(final_msg)

            except requests.RequestException as exc:
                error_msg = f"✗ REQUEST ERROR: {type(exc).__name__} - {path} (attempt {attempt + 1}/{max_retries})"
                self.logger.error(error_msg)
                if self.progress_tracker:
                    self.progress_tracker._log(error_msg)

                if attempt < max_retries - 1:
                    # Exponential backoff: 2, 4, 8, 16, 32, ... (capped at max_delay)
                    delay = min(base_delay * (2**attempt), max_delay)
                    retry_msg = (
                        f"  ⟳ RETRYING in {delay:.1f} seconds (exponential backoff)..."
                    )
                    self.logger.warning(retry_msg)
                    if self.progress_tracker:
                        self.progress_tracker._log(retry_msg)
                    time.sleep(delay)
                else:
                    final_msg = f"✗ FAILED: Max retries reached for {path}"
                    self.logger.error(final_msg)
                    if self.progress_tracker:
                        self.progress_tracker._log(final_msg)

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

        # Set progress tracker on the instance so request() can use it
        self.progress_tracker = progress_tracker

        start_index = progress_tracker.initialize(len(teams), resume=resume)

        # worlds_teams = self.get_worlds_teams()
        worlds_teams = None
        processed_count = 0
        last_committed_index = start_index - 1  # Track last index that was committed
        last_committed_team = None
        last_committed_status = None

        try:
            for i in range(start_index, len(teams)):
                team = teams[i]

                try:
                    # Determine qualification status
                    if worlds_teams and team in worlds_teams:
                        q = Qualification.WORLD
                    else:
                        q = self.get_qualifications(team)

                    # Upsert to database immediately
                    qual_obj = Qualifications(team_id=team, status=q)
                    db.upsert_quals(session, qual_obj)
                    processed_count += 1

                    # Update progress tracker for every team
                    progress_tracker.update_progress(i, team, q.name, force_save=False)

                    # Periodic commit to save progress to database
                    if processed_count % commit_interval == 0:
                        session.commit()
                        # Track what was committed
                        last_committed_index = i
                        last_committed_team = team
                        last_committed_status = q.name
                        # Save checkpoint after commit
                        progress_tracker._save_progress()
                        progress_tracker._log(
                            f"✓ CHECKPOINT: Database committed at {processed_count} teams"
                        )

                except Exception as e:
                    # Log the error but continue processing other teams
                    progress_tracker._log(
                        f"ERROR processing team {team} at index {i}: {type(e).__name__} - {e}"
                    )
                    self.logger.error(
                        "ERROR processing team %d at index %d: %s",
                        team,
                        i,
                        e,
                        exc_info=True,
                    )
                    # Continue to next team rather than stopping entire process

            # Final commit for any remaining changes
            session.commit()
            # Update progress tracker with final state
            if len(teams) > 0:
                last_idx = len(teams) - 1
                progress_tracker.update_progress(
                    last_idx, teams[last_idx], "COMPLETED", force_save=True
                )

            # Mark as complete
            progress_tracker.complete()

        except KeyboardInterrupt:
            session.commit()  # Save progress before exiting
            # Update progress tracker to reflect what was just committed
            if last_committed_index >= start_index and last_committed_team is not None:
                progress_tracker.update_progress(
                    last_committed_index,
                    last_committed_team,
                    last_committed_status or "UNKNOWN",
                    force_save=True,
                )
            progress_tracker._log(
                "INTERRUPTED: Progress committed to database. Run again to resume."
            )
            raise
        except Exception as e:
            session.commit()  # Try to save progress even on error
            # Update progress tracker to reflect what was just committed
            if last_committed_index >= start_index and last_committed_team is not None:
                progress_tracker.update_progress(
                    last_committed_index,
                    last_committed_team,
                    last_committed_status or "UNKNOWN",
                    force_save=True,
                )
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
