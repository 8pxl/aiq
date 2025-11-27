from sqlalchemy import Engine
from sqlmodel import  SQLModel, Session, create_engine
import db
from robotevents import RobotEvents
from tables import Teams
import os
from dotenv import load_dotenv


if not load_dotenv():
    print("loading .env failed")

mysqlurl = f"mysql+pymysql://root:{os.environ["MYSQL_PASSWORD"]}@127.0.0.1:3306/test"
engine = create_engine(mysqlurl, echo=True)
SQLModel.metadata.create_all(engine)

robotevents = RobotEvents(os.environ["ROBOTEVENTS_AUTH_TOKEN"])
teams = (robotevents.parse_skills())
for team in teams:
    db.upsert(engine,team)
    print("adding ", team)

# worlds_registered = robotevents.get_worlds_teams()
# if worlds_registered:
#     for team in worlds_registered:
#         db.qualify(engine, team)

# add_teams(engine, team)
