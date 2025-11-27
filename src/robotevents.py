from typing import Any
import requests
from enum import Enum

from tables import Qualification, Teams

class RobotEvents:
    token: str
    header: dict[str, str]
    base: str
    season: int

    def __init__(self, token: str):
        self.token = token
        self.base = "https://www.robotevents.com/api/v2"
        self.season = 197
        self.header = {
            "Authorization": f"Bearer {token}"
        }

    def request(self, path: str) -> Any:  # pyright: ignore[reportExplicitAny, reportAny]
        if path[0] != "/":
            print("path needs to start with a blackslash")
            return (None)
        url = self.base + path
        res = requests.get(url, headers=self.header)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            print(e)
        return res.json()  # pyright: ignore[reportAny]

    def get_qualifications(self, robotevents_id: int) -> Qualification:
        awards = self.request(f"/teams/{str(robotevents_id)}/awards?season%5B%5D={self.season}")["data"]
        highest = Qualification.NONE
        for award in awards:
            # print(award)
            if (award["qualifications"]):
                for qual in award["qualifications"]:
                    new = Qualification.from_string(qual)
                    if new.value > highest.value:
                        highest = new
        return highest


    def create_team(self, robotevents_id: int, score: tuple[int, int, int]) -> Teams:
        url = self.base + f"/teams/{robotevents_id}"
        res = requests.get(url, headers=self.header)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            print(e)
        res = res.json()  # pyright: ignore[reportAny]
        # team = Teams(
        #     id=res['id'],  # pyright: ignore[reportAny] 
        #     number=res['number'],  # pyright: ignore[reportAny]
        #     organization = res['organization'],   # pyright: ignore[reportAny]
        #     country= res['location']['country'],  # pyright: ignore[reportAny]
        #     registered = res['registered'],  # pyright: ignore[reportAny]
        #     grade = res['grade'],  # pyright: ignore[reportAny]
        #     score = score[0],
        #     programming = score[1],
        #     driver = score[2],
        #
        # )
        # return team
