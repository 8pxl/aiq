import requests

from teams import Teams

class RobotEvents:
    token: str
    header: dict[str, str]
    base: str

    def __init__(self, token: str):
        self.token = token
        self.base = "https://www.robotevents.com/api/v2"
        self.header = {
            "Authorization": f"Bearer {token}"
        }

    def get_all_teams(self) -> Teams:
        url = self.base + "/teams/170066"
        res = requests.get(url, headers=self.header)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            print(e)
        res = res.json()  # pyright: ignore[reportAny]
        team = Teams(
            id=res['id'],  # pyright: ignore[reportAny] 
            number=res['number'],  # pyright: ignore[reportAny]
            organization = res['organization'],   # pyright: ignore[reportAny]
            country= res['location']['country'],  # pyright: ignore[reportAny]
            registered = res['registered'],  # pyright: ignore[reportAny]
            grade = res['grade']  # pyright: ignore[reportAny]
        )
        return team
