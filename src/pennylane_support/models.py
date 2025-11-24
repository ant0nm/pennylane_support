from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel, Column, Computed, CheckConstraint
from sqlalchemy.dialects.postgresql import (
    ENUM as PGEnum,
    JSONB,
    VARCHAR,
    BOOLEAN,
    BIGINT,
    TIMESTAMP,
)
from typing import Optional, List
from enum import Enum
import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict


# Utils
def utcnow():
    """Returns the current time in UTC."""
    return datetime.now(timezone.utc)


# DB Models
# For the sake of consistency (C) in ACID, the data models include
# a lot of DB validations and constraints.
class Difficulty(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(primary_key=True, default=None)
    name: str = Field(unique=True)
    is_admin: bool = Field(
        default=False, sa_column=Column(BOOLEAN, server_default="false", nullable=False)
    )
    posts: List["Post"] = Relationship(back_populates="user", cascade_delete=True)


class CodingChallenge(SQLModel, table=True):
    __tablename__ = "coding_challenges"
    id: Optional[str] = Field(
        sa_column=Column(
            VARCHAR,
            CheckConstraint("id ~ '^CHAL_[0-9]+$'", name="coding_challenges_id_format"),
            primary_key=True,
            default=None,
            nullable=False,
        ),
    )
    title: str
    description: str
    category: str = Field(index=True, nullable=False)
    difficulty: Difficulty = Field(
        sa_column=Column(PGEnum(Difficulty, values_callable=lambda x: [e.value for e in x]))
    )
    points: int = Field(default=0, sa_column=Column(BIGINT, server_default="0", nullable=False))

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


class SupportConversation(SQLModel, table=True):
    __tablename__ = "support_conversations"
    id: Optional[str] = Field(
        sa_column=Column(
            VARCHAR,
            CheckConstraint("id ~ '^CONV_[0-9]+$'", name="support_conversations_id_format"),
            primary_key=True,
            default=None,
            nullable=False,
        ),
    )
    topic: str = Field(nullable=False)
    category: str = Field(index=True, nullable=False)
    coding_challenge_id: str = Field(
        foreign_key="coding_challenges.id", index=True, nullable=False, ondelete="CASCADE"
    )
    coding_challenge: CodingChallenge = Relationship(back_populates="support_conversations")
    posts: List["Post"] = Relationship(back_populates="support_conversation", cascade_delete=True)


class Post(SQLModel, table=True):
    __tablename__ = "posts"
    id: Optional[int] = Field(primary_key=True, default=None)
    timestamp: datetime = Field(
        default_factory=utcnow,
        sa_column=Column(TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    content: str = Field(nullable=False)
    user_id: int = Field(foreign_key="users.id", index=True, nullable=False, ondelete="CASCADE")
    user: User = Relationship(back_populates="posts")
    support_conversation_id: str = Field(
        foreign_key="support_conversations.id", index=True, nullable=False, ondelete="CASCADE"
    )
    support_conversation: SupportConversation = Relationship(back_populates="posts")


# API Models
class CodingChallengeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    category: str
    difficulty: str
    points: int
    tags: List[str]
    learning_objectives: List[str]
    hints: List[str]
