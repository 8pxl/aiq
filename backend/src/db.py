from datetime import datetime
import os
import sys
import getpass
from typing import Any
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine, select
from tables import Qualification, Qualifications, Teams, Metadata, User
from dotenv import load_dotenv

if not load_dotenv():
    print("Warning: .env file not found or failed to load")

# Get MySQL password - from environment or stdin
mysql_password = os.environ.get("MYSQL_PASSWORD")
if not mysql_password:
    print("\nMYSQL_PASSWORD not found in environment.")
    print("Please enter your MySQL password:")
    try:
        # Use getpass for password input (hides input)
        mysql_password = getpass.getpass("> ")
        if not mysql_password:
            print("Error: MySQL password cannot be empty")
            sys.exit(1)
    except (EOFError, KeyboardInterrupt):
        print("\nError: Password input cancelled")
        sys.exit(1)

mysqlurl = f"mysql+pymysql://fastapi_user:{mysql_password}@127.0.0.1:3306/aiq"
engine = create_engine(mysqlurl, echo=False)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def number_to_id(session: Session, number: str) -> int:
    return session.exec(select(Teams.id).where(Teams.number == number)).one()


def get_all_teams(session: Session) -> list[int]:
    ids = []
    return list(
        session.exec(
            select(Teams.id)
            # .where(Teams.region == "California - Region 4")
            # .where(Teams.grade == "High School")
        ).all()
    )


def upsert(session: Session, x: Any):
    _ = session.merge(x)
    session.commit()


def upsert_quals(session: Session, x: Qualifications):
    qual = session.get(Qualifications, x.team_id)
    if not qual:
        session.add(x)
    else:
        qual.status = Qualification(max(qual.status.value, x.status.value))
    session.commit()


def update_quals(session: Session, x: Qualifications):
    qual = session.get(Qualifications, x.team_id)
    if not qual:
        session.add(x)
    else:
        qual.status = x.status
    session.commit()


def qualify(session: Session, id: int):
    existing = session.get(Teams, id)
    if not existing:
        print(f"team {id} doesnt exist yet!")
        return
    else:
        existing.qualification = Qualification.WORLD
    session.commit()


def set_update_time(session: Session):
    metadata = session.get(Metadata, 1)
    if not metadata:
        print("metadata doesnt exist!")
        return
        # metadata =Metadata(id=1, last_slow_update=datetime.now())
        # session.add(metadata)
    metadata.last_slow_update = datetime.now()
    session.commit()


def get_last_slow_update(session: Session) -> datetime:
    return session.exec(select(Metadata.last_slow_update)).one()


def user_has_perms(session: Session, user_id: str) -> bool:
    return user_id in session.exec(select(User.id))
