from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel, Column, Computed
from sqlalchemy.dialects.postgresql import JSONB, VARCHAR, ENUM as PGEnum
from typing import Optional, List
from enum import Enum
import sqlalchemy as sa


# Utils
def utcnow():
    """Returns the current time in UTC."""
    return datetime.now(timezone.utc)


# Models
# Simpifying assumptions:
# - All primary keys will be auto-incrementing integers. Custom IDs like
# "CHAL_001", "CONV_001" can then be implemented using stored generated columns in PostgreSQL.
class Difficulty(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)


class User(BaseModel, table=True):
    __tablename__ = "users"
    name: str
    is_admin: bool = Field(
        default=False, sa_column=Column(sa.Boolean(), server_default="false", nullable=False)
    )


class CodingChallenge(BaseModel, table=True):
    __tablename__ = "coding_challenges"
    challenge_id: Optional[str] = Field(
        sa_column=Column(
            VARCHAR,
            Computed(
                (
                    "CASE "
                    "WHEN id <= 999 THEN 'CHAL_' || LPAD(id::VARCHAR, 3, '0') "
                    "ELSE 'CHAL_' || id::VARCHAR "
                    "END"
                ),
                persisted=True,
            ),
            index=True,
            nullable=False,
            unique=True,
        ),
    )
    title: str
    description: str
    category: str = Field(index=True, nullable=False)
    difficulty: Difficulty = Field(
        sa_column=Column(PGEnum(Difficulty, values_callable=lambda x: [e.value for e in x]))
    )
    points: int = Field(
        default=0, sa_column=Column(sa.Integer(), server_default="0", nullable=False)
    )

    tags: List[str] = Field(
        sa_column=Column(JSONB, nullable=False, server_default="[]"), default_factory=list
    )
    learning_objectives: List[str] = Field(
        sa_column=Column(JSONB, nullable=False, server_default="[]"), default_factory=list
    )
    hints: List[str] = Field(
        sa_column=Column(JSONB, nullable=False, server_default="[]"), default_factory=list
    )
    support_conversations: List["SupportConversation"] = Relationship(
        back_populates="coding_challenge", cascade_delete=True
    )


class SupportConversation(BaseModel, table=True):
    __tablename__ = "support_conversations"
    conversation_id: Optional[str] = Field(
        sa_column=Column(
            VARCHAR,
            Computed(
                (
                    "CASE "
                    "WHEN id <= 999 THEN 'CONV_' || LPAD(id::VARCHAR, 3, '0') "
                    "ELSE 'CONV_' || id::VARCHAR "
                    "END"
                ),
                persisted=True,
            ),
            index=True,
            nullable=False,
            unique=True,
        ),
    )
    topic: str = Field(nullable=False)
    category: str = Field(index=True, nullable=False)
    coding_challenge_id: int = Field(
        foreign_key="coding_challenges.id", index=True, nullable=False, ondelete="CASCADE"
    )
    coding_challenge: CodingChallenge = Relationship(back_populates="support_conversations")
    posts: List["Post"] = Relationship(back_populates="support_conversation", cascade_delete=True)


class Post(BaseModel, table=True):
    __tablename__ = "posts"
    timestamp: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    support_conversation_id: int = Field(
        foreign_key="support_conversations.id", index=True, nullable=False, ondelete="CASCADE"
    )
    support_conversation: SupportConversation = Relationship(back_populates="posts")
