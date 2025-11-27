from sqlalchemy import Engine
from sqlmodel import  SQLModel, Session, create_engine
from robotevents import RobotEvents
from teams import Teams
import os
from dotenv import load_dotenv


if not load_dotenv():
    print("loading .env failed")

mysqlurl = "mysql+pymysql://root:i am the state@127.0.0.1:3306/test"
engine = create_engine(mysqlurl, echo=True)
SQLModel.metadata.create_all(engine)

def add_teams(engine: Engine, team: Teams):
    session = Session(engine)
    exisisting = session.get(Teams, team.id)
    if not exisisting:
        session.add(team)
        session.commit()

robotevents = RobotEvents(os.environ["ROBOTEVENTS_AUTH_TOKEN"])
team = robotevents.get_all_teams()
add_teams(engine, team)
