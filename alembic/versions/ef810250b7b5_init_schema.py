"""init_schema

Revision ID: ef810250b7b5
Revises:
Create Date: 2025-11-23 19:02:11.341507

"""

# Auto-generated with `alembic revision --autogenerate -m "init_schema"` with a few
# minor changes.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "ef810250b7b5"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "coding_challenges",
        sa.Column("id", sa.VARCHAR(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("category", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "difficulty",
            postgresql.ENUM("Beginner", "Intermediate", "Advanced", name="difficulty"),
            nullable=True,
        ),
        sa.Column("points", sa.BIGINT(), server_default="0", nullable=False),
        sa.Column(
            "tags", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False
        ),
        sa.Column(
            "learning_objectives",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column(
            "hints", postgresql.JSONB(astext_type=sa.Text()), server_default="[]", nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_coding_challenges_category"), "coding_challenges", ["category"], unique=False
    )
    op.create_check_constraint(
        "coding_challenges_id_format", "coding_challenges", "id ~ '^CHAL_[0-9]+$'"
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_admin", sa.BOOLEAN(), server_default="false", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "support_conversations",
        sa.Column("id", sa.VARCHAR(), nullable=False),
        sa.Column("topic", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("category", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("coding_challenge_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["coding_challenge_id"], ["coding_challenges.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_support_conversations_category"),
        "support_conversations",
        ["category"],
        unique=False,
    )
    op.create_index(
        op.f("ix_support_conversations_coding_challenge_id"),
        "support_conversations",
        ["coding_challenge_id"],
        unique=False,
    )
    op.create_check_constraint(
        "support_conversations_id_format", "support_conversations", "id ~ '^CONV_[0-9]+$'"
    )
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "timestamp",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("support_conversation_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(
            ["support_conversation_id"], ["support_conversations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_posts_support_conversation_id"), "posts", ["support_conversation_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_posts_support_conversation_id"), table_name="posts")
    op.drop_table("posts")
    op.drop_index(
        op.f("ix_support_conversations_coding_challenge_id"), table_name="support_conversations"
    )
    op.drop_index(op.f("ix_support_conversations_category"), table_name="support_conversations")
    op.drop_table("support_conversations")
    op.drop_table("users")
    op.drop_index(op.f("ix_coding_challenges_category"), table_name="coding_challenges")
    op.drop_table("coding_challenges")
    op.execute("DROP TYPE difficulty")
