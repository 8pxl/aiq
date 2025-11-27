from datetime import datetime, timedelta
from sqlalchemy import Engine
from sqlmodel import  SQLModel, Session, create_engine
import db
from robotevents import RobotEvents
from tables import Teams, Qualifications
import os
from dotenv import load_dotenv


if not load_dotenv():
    print("loading .env failed")

mysqlurl = f"mysql+pymysql://root:{os.environ["MYSQL_PASSWORD"]}@127.0.0.1:3306/test"
engine = create_engine(mysqlurl, echo=True)
SQLModel.metadata.create_all(engine)

print("fast step")
robotevents = RobotEvents(os.environ["ROBOTEVENTS_AUTH_TOKEN"])
teams = (robotevents.parse_skills())
for team in teams:
    db.upsert(engine,team)
    print("adding ", team)

if db.get_last_qualification_update(engine) - datetime.now() > timedelta(weeks=1):
    all_teams = db.get_all_teams(engine)
    qualifications  = robotevents.create_qualifications_full(all_teams)
    print("updating qualifications!")
    for q in qualifications:
        db.upsert(engine, q)
# self.create_qualifications_worlds_fast()
