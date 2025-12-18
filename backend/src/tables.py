from __future__ import annotations
from datetime import datetime
from sqlalchemy.orm import Mapped
from typing_extensions import Optional
from sqlmodel import Column, Field, ForeignKey, Integer, Relationship, SQLModel
from enum import Enum

class Qualification(Enum):
    NONE = 0
    REGIONAL = 1
    WORLD = 2

    @classmethod
    def from_string(cls, s: str) -> Qualification:
        mapping = {
            "Event Region Championship": cls.REGIONAL,
            "World Championship": cls.WORLD
        }
        return mapping.get(s, cls.NONE)

class Metadata(SQLModel,table=True):
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


