import logging
from typing import Any
import requests
from enum import Enum
import db
from tables import Qualification, Teams

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
        self.header = {
            "Authorization": f"Bearer {token}"
        }

    def request(self, path: str) -> Any | None:  # pyright: ignore[reportExplicitAny]
        if not path.startswith("/"):
            self.logger.exception("path needs to start with a blackslash")
            return (None)
        url = self.base + path
        res = requests.get(url, headers=self.header)
        try:
            res.raise_for_status()
        except requests.RequestException as exc:
            self.logger.exception("API request failed: %s %s", url, exc)
            return None
        return res.json()  # pyright: ignore[reportAny]

    def get_qualifications(self, robotevents_id: int) -> Qualification:
        awards = self.request(f"/teams/{str(robotevents_id)}/awards?season%5B%5D={self.season}")
        if not awards:
            return Qualification.NONE
        awards = awards["data"]
        highest = Qualification.NONE
        for award in awards:
            # print(award)
            if (award["qualifications"]):
                for qual in award["qualifications"]:
                    new = Qualification.from_string(qual)
                    if new.value > highest.value:
                        highest = new
        return highest


    def create_team(self, robotevents_id: int, rank: int, score:int, programming: int, driver: int):
        res = self.request(f"/teams/{robotevents_id}")
        if not res:
            return None
        team = Teams(
            id = res['id'],  # pyright: ignore[reportAny] 
            number = res['number'],  # pyright: ignore[reportAny]
            organization = res['organization'],   # pyright: ignore[reportAny]
            country = res['location']['country'],  # pyright: ignore[reportAny]
            registered = res['registered'],  # pyright: ignore[reportAny]
            grade = res['grade'],  # pyright: ignore[reportAny]
            qualification = self.get_qualifications(res['id']),  # pyright: ignore[reportAny]
            world_rank = rank,
            score = score,
            programming = programming,
            driver = driver
        )
        return team

    def parse_skills(self) ->list[Teams]:
        url = "https://www.robotevents.com/api/seasons/197/skills?post_season=0&grade_level=High%20School"
        res = requests.get(url)
        try:
            res.raise_for_status()
        except requests.RequestException as exc:
            self.logger.exception("API request failed: %s %s", url, exc)
        res = res.json()
        # print("request went through!")
        # print(res)
        teams = []
        for team in res:
            id: int = team["team"]["id"]
            rank: int = team["rank"]
            score =team["scores"]["score"]
            programming = team["scores"]["programming"]
            driver = team["scores"]["driver"]
            teams.append(self.create_team(id, rank, score, programming, driver))
            if (len(teams) >= 5):
                break
        return teams
