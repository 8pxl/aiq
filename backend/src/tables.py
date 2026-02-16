from __future__ import annotations
from datetime import datetime
from sqlmodel import (
    Column,
    DateTime,
    Field,
    ForeignKey,
    Integer,
    Relationship,
    SQLModel,
)

from enum import IntEnum


class Qualification(IntEnum):
    NONE = 0
    REGIONAL = 1
    WORLD = 2

    @classmethod
    def from_string(cls, s: str) -> Qualification:
        mapping = {
            "Event Region Championship": cls.REGIONAL,
            "World Championship": cls.WORLD,
        }
        return mapping.get(s, cls.NONE)


class Metadata(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    last_slow_update: datetime = datetime.now()


class Qualifications(SQLModel, table=True):
    team_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("teams.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )
    status: Qualification
    team: Teams = Relationship(back_populates="qualification_status")


class Teams(SQLModel, table=True):
    id: int = Field(primary_key=True)
    number: str
    organization: str
    country: str
    region: str
    grade: str
    # qualification: Qualification
    world_rank: int
    score: int
    programming: int
    driver: int
    qualification_status: Qualifications = Relationship(back_populates="team")


class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    email: str = Field(sa_column_kwargs={"unique": True})
    emailVerified: bool
    image: str | None = None
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)


class Session(SQLModel, table=True):
    id: str = Field(primary_key=True)
    expiresAt: datetime
    token: str = Field(sa_column_kwargs={"unique": True})
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)
    ipAddress: str | None = None
    userAgent: str | None = None
    userId: str = Field(foreign_key="user.id", ondelete="CASCADE")


class Account(SQLModel, table=True):
    id: str = Field(primary_key=True)
    accountId: str
    providerId: str
    userId: str = Field(foreign_key="user.id", ondelete="CASCADE")
    accessToken: str | None = None
    refreshToken: str | None = None
    idToken: str | None = None
    accessTokenExpiresAt: datetime | None = None
    refreshTokenExpiresAt: datetime | None = None
    scope: str | None = None
    password: str | None = None  # Hashed password
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)
