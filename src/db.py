from sqlalchemy import Engine
from sqlmodel import Session
from tables import Teams


def add_team(engine: Engine, team: Teams):
    session = Session(engine)
    exisisting = session.get(Teams, team.id)
    if not exisisting:
        session.add(team)
        session.commit()

