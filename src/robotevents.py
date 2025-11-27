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


    # def create_team(self, robotevents_id: int,res: any, rank: int, score:int, programming: int, driver: int):
    #     res = self.request(f"/teams/{robotevents_id}")
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

    def parse_skills(self) ->list[Teams]:
        url = f"https://www.robotevents.com/api/seasons/{self.season}/skills?post_season=0&grade_level=High%20School"
        res = requests.get(url)
        try:
            res.raise_for_status()
        except requests.RequestException as exc:
            self.logger.exception("API request failed: %s %s", url, exc)
        res = res.json()
        teams = []
        for team in res:
            print("adding team ", team['number'])
            country: str = res['location']['country'],  # pyright: ignore[reportAny, reportAssignmentType]
            region: str| None = res['location']['region']
            if not region:
                region = country
            teams.append(Teams(
                id =team['id'],  # pyright: ignore[reportAny] 
                number = team['number'],  # pyright: ignore[reportAny]
                organization =team['organization'],   # pyright: ignore[reportAny]
                country = country,
                region = region,
                registered = team['registered'],  # pyright: ignore[reportAny]
                grade = res['grade'],  # pyright: ignore[reportAny]
                qualification = self.get_qualifications(res['id']),  # pyright: ignore[reportAny]
                world_rank = team["rank"],
                score = team["scores"]["score"],
                programming = team["scores"]["programming"],
                driver = team["scores"]["driver"]
            ))
            if (len(teams) >=100):
                break
        return teams

    def get_worlds_teams(self) -> list[int] | None:
        event = "/events/58909/teams"
        res= self.request(event)
        if not res:
            return None
        pages = res["meta"]["last_page"]
        print(pages)
        teams= []
        for i in range(1, pages + 1):
            if (i >= 2):
                break
            res= self.request(event+ f"?page={i}")
            if not res:
                continue
            res = res["data"] 
            page = 1
            print(len(res))
            for team in res: 
                teams.append(team["id"])
        return teams


