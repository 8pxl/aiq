from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query, status
from sqlalchemy.orm import query
from sqlmodel import Session, select
from typing import Annotated

from api import auth
import db
from tables import Qualification, Qualifications, Teams

from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    number: str
    status: Qualification
    organization: str
    country: str
    region: str
    world_rank: int
    score: int
    driver: int
    programming: int

class TeamQualificationOut(BaseModel):
    number: str
    organization: str
    status: Qualification


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/teams")
def get_teams(
    session: Session = Depends(db.get_session), _=Depends(auth.authenticate_user)
):
    print("getting ateams ts")
    return {"code": 200, "result": db.get_all_teams(session)}

@app.get("/regions")
def get_regions(session: Session = Depends(db.get_session)):
    query = select(Teams.region).distinct().order_by(Teams.region)
    rows = session.exec(query).all()
    return rows


@app.get("/lb")
def get_leaderboard(
    grade: str = "High School",
    region: str | None = None,
    exclude_statuses: Annotated[list[Qualification], Query()] = [Qualification.NONE],
    limit: int = 20,
    session: Session = Depends(db.get_session),
):
    query = (
        select(
            Teams.number,
            Qualifications.status,
            Teams.organization,
            Teams.country,
            Teams.region,
            Teams.world_rank,
            Teams.score,
            Teams.driver,
            Teams.programming,
        )
        .join(Qualifications)
        .where(Teams.grade == grade)
        .order_by(Teams.world_rank)
        .limit(limit)
    )

    for excluded_status in exclude_statuses:
        query = query.where(Qualifications.status != excluded_status)
    
    if region is not None:
        query = query.where(Teams.region == region)

    rows = session.exec(query).all()

    result = [
        LeaderboardEntry(
            number=number,
            status=qual_status, 
            organization=organization,
            country=country,
            region=reg,
            world_rank=world_rank,
            score=score,
            driver=driver,
            programming=programming,
        )
        for number, qual_status, organization, country, reg, world_rank, score, driver, programming in rows
    ]

    return {"code": 200, "result": result}


@app.get("/qualifications")
def get_qualifications(
    session: Session = Depends(db.get_session), _=Depends(auth.authenticate_user)
):
    stmt = select(
        Teams.number,
        Teams.organization,
        Qualifications.status,
    ).join(Qualifications)

    rows = session.exec(stmt).all()

    return [
        TeamQualificationOut(
            number=number,
            organization=organization,
            status=status,  # pyright: ignore[reportArgumentType]
        )
        for number, organization, status in rows
    ]


@app.put("/qualifications")
def put_qualifications(
    team: str,
    status: Qualification,
    session: Session = Depends(db.get_session),
    _=Depends(auth.authenticate_user),
):
    try:
        db.update_quals(
            session, Qualifications(team_id=db.number_to_id(session, team), status=status)
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Hello World"}
