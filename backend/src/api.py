from fastapi import APIRouter, Depends, FastAPI
from sqlmodel import Session, select

import db
from tables import Qualification, Qualifications, Teams

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
def get_teams(session: Session = Depends(db.get_session)):
    return {"code": 1000, "result": db.get_all_teams(session)}

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
@app.put("/qualification")
def put_qualification(
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
