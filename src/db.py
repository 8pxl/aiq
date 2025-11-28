from datetime import datetime
import os
from typing import Any
from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine, select
from tables import Qualification, Qualifications, Teams, Metadata
from dotenv import load_dotenv

if not load_dotenv():
    print("loading .env failed")

mysqlurl = f"mysql+pymysql://root:{os.environ["MYSQL_PASSWORD"]}@127.0.0.1:3306/test"
engine = create_engine(mysqlurl, echo=True)
SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def number_to_id(engine: Engine, number: str) -> int:
    with Session(engine) as session:
        return session.exec(select(Teams.id).where(Teams.number==number)).one()

def get_all_teams(engine: Engine) -> list[int]:
    ids = []
    with Session(engine) as session:
        return list(session.exec(select(Teams.id).where(Teams.region=="California - Region 4").where(Teams.grade=="High School")).all())

def upsert(engine: Engine, x: Any):
    with Session(engine) as session:
        _ = session.merge(x)
        session.commit()

def upsert_quals(engine: Engine, x: Qualifications):
    with Session(engine) as session:
        qual = session.get(Qualifications, x.team_id)
        if not qual:
            session.add(x)
        else:
            qual.status = Qualification(max(qual.status.value, x.status.value))
        session.commit()

def qualify(engine: Engine, id: int):
    with Session(engine) as session:
        existing = session.get(Teams,id)
        if not existing:
            print(f"team {id} doesnt exist yet!")
            return
        else:
            existing.qualification = Qualification.WORLD
        session.commit();

def set_update_time(engine: Engine):
    with Session(engine) as session:
        metadata = session.get(Metadata, 1)
        if not metadata:
            print("metadata doesnt exist!")
            return
            # metadata =Metadata(id=1, last_slow_update=datetime.now())
            # session.add(metadata)
        metadata.last_slow_update = datetime.now()
        session.commit()



def get_last_slow_update(engine: Engine)-> datetime: 
    with Session(engine) as session:
        return(session.exec(select(Metadata.last_slow_update)).one())

    # existing = session.get(Teams, team.id)
    #     if not existing:
    #         session.add(team)
    #     else:
    #         existing.score = team.score
    #         existing.driver = team.driver
    #         existing.rank = team.world_rank
    #         existing.programming = team.programming
    #         existing.qualification = team.qualification
    #     session.commit()
