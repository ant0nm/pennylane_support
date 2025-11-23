from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


# Utils
def utcnow():
    """Returns the current time in UTC."""
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    id: int = Field(primary_key=True, nullable=False)
    name: str
    is_admin: bool = Field(default=False)
