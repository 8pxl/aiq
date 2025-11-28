from datetime import datetime, timedelta
from sqlalchemy import Engine
from sqlmodel import  SQLModel, Session, create_engine
import db
from robotevents import RobotEvents
from tables import Qualification, Teams, Qualifications
import os
from dotenv import load_dotenv
from fastapi import FastAPI

app = FastAPI()

if not load_dotenv():
    print("loading .env failed")


# print("fast step")
robotevents = RobotEvents(os.environ["ROBOTEVENTS_AUTH_TOKEN"])
SQLModel.metadata.create_all(db.engine)

# db.set_update_time(engine)
# teams = robotevents.parse_skills(True)
# for team in teams:
#     db.upsert(engine,team)
#     print("adding ", team)

# print(robotevents.create_qualifications_sig())

# qualifications = robotevents.create_qualifications_sig()
# if qualifications:
#     for q in qualifications:
#         db.upsert_quals(engine, q)

#
# print(datetime.now()-db.get_last_slow_update(engine) > timedelta(seconds=60))
# 169926
# 186744

# all_teams = db.get_all_teams(engine)
# qualifications  = robotevents.create_qualifications_full(all_teams)
# print("updating qualifications!")
# for q in qualifications:
#     db.upsert_quals(engine, q)

# manual_qualifications = ["15442A", "2054V", "16689A", "6008G", "884A", "3004A"]
#
# for id in [db.number_to_id(engine, number) for number in manual_qualifications]:
#     db.upsert_quals(engine, Qualifications(
#         team_id = id,
#         status = Qualification.WORLD
#     ))

# self.create_qualifications_worlds_fast()
#

@app.get("/")
async def root():
    return {"message": "Hello World"}
