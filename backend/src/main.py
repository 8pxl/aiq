from datetime import datetime, timedelta
import time
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine
import db
from robotevents import RobotEvents
from tables import Qualification, Teams, Qualifications
from progress_tracker import ProgressTracker
import os
import sys
from fastapi import FastAPI
from api.api import *
from dotenv import load_dotenv

# Load .env file
if not load_dotenv():
    print("Warning: .env file not found or failed to load")

# Get RobotEvents token - from environment or stdin
robotevents_token = os.environ.get("ROBOTEVENTS_AUTH_TOKEN")
if not robotevents_token:
    print("\nROBOTEVENTS_AUTH_TOKEN not found in environment.")
    print("Please enter your RobotEvents API token:")
    try:
        robotevents_token = input("> ").strip()
        if not robotevents_token:
            print("Error: Token cannot be empty")
            sys.exit(1)
    except (EOFError, KeyboardInterrupt):
        print("\nError: Token input cancelled")
        sys.exit(1)

# print("fast step")
# Create progress tracker for the long-running qualification creation
progress_tracker = ProgressTracker(log_file="qualification_progress.log")

# Initialize RobotEvents with progress tracker for API request logging
robotevents = RobotEvents(robotevents_token, progress_tracker=progress_tracker)
SQLModel.metadata.create_all(db.engine)


with Session(db.engine) as session:
    # qualifications = robotevents.create_qualifications_sig()
    # if qualifications:
    #     print(f"Processing {len(qualifications)} signature event qualifications...")
    #     for q in qualifications:
    #         db.upsert_quals(session, q)
    #     session.commit()
    #     print("Signature event qualifications completed!")
    #
    # failed = [51097, 113192, 119951,172903, 178864,193590]

    delta = datetime.now() - db.get_last_slow_update(session)
    if delta > timedelta(days = 7):
        print("last update was: ", db.get_last_slow_update(session))
        all_teams = db.get_all_teams(session)
        print(f"\nProcessing qualifications for {len(all_teams)} teams...")

        # This now commits to DB periodically, so no need to return qualifications list
        # 
        processed_count = robotevents.create_qualifications_full(
            session=session,  # Pass session for database operations
            teams=all_teams,
            resume=True,  # Enable resumption from last checkpoint
            progress_tracker=progress_tracker,
            commit_interval=10,  # Commit every 10 teams
        )

        print(f"Qualification creation completed! Processed {processed_count} teams.")

        # Update metadata timestamp
        db.set_update_time(session)

#     manual_qualifications = ["15442A", "2054V", "16689A", "6008G", "884A", "3004A", "8917B"]
# #
#     for id in [db.number_to_id(session, number) for number in manual_qualifications]:
#         db.upsert_quals(session, Qualifications(
#             team_id = id,
#             status = Qualification.WORLD
#         ))

# self.create_qualifications_worlds_fast()
#
