from fastapi import APIRouter, Depends, FastAPI, Header
from sqlmodel import Session, select

from api import auth
import db
from tables import Qualification, Qualifications, Teams

from pydantic import BaseModel


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
def get_teams(session: Session = Depends(db.get_session),
    _ = Depends(auth.authenticate_user)):
    return {"code":200, "result": db.get_all_teams(session)}

@app.get("/lb")
def get_leaderboard(
    ms: bool = False,
    region: str | None = None,
    session: Session = Depends(db.get_session)):
    query = select(Teams)
    if ms:
        query = query.where(Teams.grade == "Middle School")
    return {
        "code": 1000,
        "message": session.exec(query)
    }

@app.get("/qualifications")
def get_qualifications(session: Session = Depends(db.get_session),
                       _ = Depends(auth.authenticate_user)):
    stmt = (
        select(  # pyright: ignore[reportCallIssue, reportUnknownMemberType]
            Teams.number,
            Teams.organization,
            Qualifications.status,  # pyright: ignore[reportArgumentType]
        )
        .join(Qualifications)
    )

    rows = session.exec(stmt).all()

    return [
        TeamQualificationOut(
            number=number,
            organization=organization,
            status=status,
        )
        for number, organization, status in rows
    ]

@app.put("/qualifications")
def put_qualifications(
    team: int,
    s: str,
    session: Session = Depends(db.get_session)):
    status: Qualification = Qualification.NONE
    match s.lower():
        case "regional":
            status = Qualification.REGIONAL
        case "world":
            status = Qualification.WORLD
        case _:
            status = Qualification.NONE
    db.update_quals(session, Qualifications(team_id = team, status = status))
        
@app.get("/")
async def root():
    return {"message": "Hello World"}
