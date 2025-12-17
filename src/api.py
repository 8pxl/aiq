from fastapi import APIRouter, Depends, FastAPI
from sqlmodel import Session, select

import db
from tables import Teams

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
    return {"teams": db.get_all_teams(session)}

@app.get("/teams")
def get_leaderboard(
    ms: bool = False,
    region: str | None = None,
    session: Session = Depends(db.get_session)):
    query = select(Teams)
    if ms:
        query = query.where(Teams.grade == "Middle School")
    return {
        "teams": session.exec(query)
    }

@app.get("/")
async def root():
    return {"message": "Hello World"}
