from datetime import datetime, timedelta
import time
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine
import db
from robotevents import RobotEvents
from tables import Qualification, Teams, Qualifications
from progress_tracker import ProgressTracker
import os
from fastapi import FastAPI
from api.api import *
from dotenv import load_dotenv

if not load_dotenv():
    print("loading .env failed")


# print("fast step")
robotevents = RobotEvents(os.environ["ROBOTEVENTS_AUTH_TOKEN"])
SQLModel.metadata.create_all(db.engine)

# Create progress tracker for the long-running qualification creation
progress_tracker = ProgressTracker(log_file="qualification_progress.log")

# print("\n" + "=" * 80)
# print("Starting qualification creation process (this may take over 1 hour)")
# print("Progress will be logged to: qualification_progress.log")
# print("Progress checkpoint saved to: qualification_progress.json")
# print("You can safely interrupt and resume this process.")
# print("=" * 80 + "\n")

with Session(db.engine) as session:
    # First, create qualifications from signature events
    qualifications = robotevents.create_qualifications_sig()
    if qualifications:
        for q in qualifications:
            db.upsert_quals(session, q)

    # Then, create qualifications for all teams (long-running process)
    all_teams = db.get_all_teams(session)
    qualifications = robotevents.create_qualifications_full(
        all_teams,
        resume=True,  # Enable resumption from last checkpoint
        progress_tracker=progress_tracker,
    )

    print("Updating database with qualifications...")
    for q in qualifications:
        db.upsert_quals(session, q)

    print("Qualification creation completed!")

# manual_qualifications = ["15442A", "2054V", "16689A", "6008G", "884A", "3004A"]
#
# for id in [db.number_to_id(engine, number) for number in manual_qualifications]:
#     db.upsert_quals(engine, Qualifications(
#         team_id = id,
#         status = Qualification.WORLD
#     ))

# self.create_qualifications_worlds_fast()
#
