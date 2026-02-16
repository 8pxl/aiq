from typing import Annotated
import os

from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
    Cookie,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import query
from sqlmodel import Session, select
from pydantic import BaseModel

from api.auth_native import (
    LoginRequest,
    SignUpRequest,
    SessionResponse,
    get_current_user,
    get_session,
    login,
    logout,
    require_auth,
    sign_up,
)
import db
from tables import Qualification, Qualifications, Teams, User


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

# CORS Configuration
# TODO: Update allow_origins to your specific domains in production
# Example: allow_origins=["https://your-app.netlify.app", "http://localhost:3000"]
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth routes
@app.post("/auth/sign-in", response_model=SessionResponse)
async def sign_in_endpoint(
    request: Request,
    login_data: LoginRequest,
    response: Response,
    session: Session = Depends(db.get_session),
):
    return await login(request, login_data, response, session)


@app.post("/auth/sign-out")
async def sign_out_endpoint(
    response: Response,
    session: Session = Depends(db.get_session),
    access_token: str | None = Cookie(None),
):
    return await logout(response, session, access_token)


@app.get("/auth/session", response_model=SessionResponse)
async def get_auth_session(
    current_user: Annotated[User | None, Depends(get_current_user)],
):
    return await get_session(current_user)


# Optional: signup endpoint (you can remove this if not needed)
@app.post("/auth/sign-up", response_model=SessionResponse)
async def sign_up_endpoint(
    request: Request,
    signup_data: SignUpRequest,
    response: Response,
    session: Session = Depends(db.get_session),
):
    return await sign_up(request, signup_data, response, session)


# Protected endpoints
@app.get("/teams")
def get_teams(
    session: Session = Depends(db.get_session),
    _: User = Depends(require_auth),
):
    print("getting teams")
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
def get_qualifications(session: Session = Depends(db.get_session)):
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


@app.get("/lastSlow")
def get_last_slow(
    session: Session = Depends(db.get_session),
    _: User = Depends(require_auth),
):
    return db.get_last_slow_update(session)


# @app.post("/update")
# def trigger_update(
#     session: Session = Depends(db.get_session),
#         _: User = Depends(require_auth)):
#     pass


@app.put("/qualifications")
def put_qualifications(
    team: str,
    status: Qualification,
    session: Session = Depends(db.get_session),
    _: User = Depends(require_auth),
):
    try:
        db.update_quals(
            session,
            Qualifications(team_id=db.number_to_id(session, team), status=status),
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
async def root():
    return {"message": "Hello World"}
