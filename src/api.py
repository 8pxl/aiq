from fastapi import APIRouter, Depends
from sqlmodel import Session

import db

router = APIRouter()

@router.get("/teams")
def get_teams(session: Session = Depends(db.get_session)):
    return {"teams": db.get_all_teams(session)}
