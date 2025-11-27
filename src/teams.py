from sqlmodel import Field, SQLModel


class Teams(SQLModel, table=True):
    id: int = Field(primary_key=True)
    number: str
    organization: str
    country: str
    registered: bool
    grade: str

