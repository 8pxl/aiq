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

# with Session(db.engine) as session:
#     # # First, create qualifications from signature events
#     # qualifications = robotevents.create_qualifications_sig()
#     # if qualifications:
#     #     print(f"Processing {len(qualifications)} signature event qualifications...")
#     #     for q in qualifications:
#     #         db.upsert_quals(session, q)
#     #     session.commit()
#     #     print("Signature event qualifications completed!")
#     #
#     # # Then, create qualifications for all teams (long-running process)
#     all_teams = db.get_all_teams(session)
#     print(f"\nProcessing qualifications for {len(all_teams)} teams...")
#
#     # This now commits to DB periodically, so no need to return qualifications list
#     processed_count = robotevents.create_qualifications_full(
#         session=session,  # Pass session for database operations
#         teams=all_teams,
#         resume=True,  # Enable resumption from last checkpoint
#         progress_tracker=progress_tracker,
#         commit_interval=10,  # Commit every 10 teams
#     )
#
#     print(f"Qualification creation completed! Processed {processed_count} teams.")
#
#     # Update metadata timestamp
#     db.set_update_time(session)
#
# # manual_qualifications = ["15442A", "2054V", "16689A", "6008G", "884A", "3004A"]
# #
# # for id in [db.number_to_id(engine, number) for number in manual_qualifications]:
# #     db.upsert_quals(engine, Qualifications(
# #         team_id = id,
# #         status = Qualification.WORLD
# #     ))
#
# # self.create_qualifications_worlds_fast()
# #
