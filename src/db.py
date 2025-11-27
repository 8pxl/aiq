from sqlalchemy import Engine
from sqlmodel import Session
from tables import Qualification, Teams


def upsert(engine: Engine, team: Teams):
    with Session(engine) as session:
        _ = session.merge(team)
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
