"""init_schema

Revision ID: f99bb9bac202
Revises:
Create Date: 2025-11-23 14:45:07.581659

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "f99bb9bac202"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "coding_challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "challenge_id",
            sa.VARCHAR(),
            sa.Computed(
                (
                    "CASE "
                    "WHEN id <= 999 THEN 'CHAL_' || LPAD(id::VARCHAR, 3, '0') "
                    "ELSE 'CHAL_' || id::VARCHAR "
                    "END"
                ),
                persisted=True,
            ),
            nullable=False,
        ),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("category", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "difficulty",
            postgresql.ENUM("Beginner", "Intermediate", "Advanced", name="difficulty"),
            nullable=True,
        ),
        sa.Column("points", sa.Integer(), server_default="0", nullable=False),
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
    op.create_index(
        op.f("ix_coding_challenges_challenge_id"),
        "coding_challenges",
        ["challenge_id"],
        unique=True,
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default="false", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "support_conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "conversation_id",
            sa.VARCHAR(),
            sa.Computed(
                (
                    "CASE "
                    "WHEN id <= 999 THEN 'CONV_' || LPAD(id::VARCHAR, 3, '0') "
                    "ELSE 'CONV_' || id::VARCHAR "
                    "END"
                ),
                persisted=True,
            ),
            nullable=False,
        ),
        sa.Column("topic", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("category", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("coding_challenge_id", sa.Integer(), nullable=False),
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
    op.create_index(
        op.f("ix_support_conversations_conversation_id"),
        "support_conversations",
        ["conversation_id"],
        unique=True,
    )
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("support_conversation_id", sa.Integer(), nullable=False),
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
        op.f("ix_support_conversations_conversation_id"), table_name="support_conversations"
    )
    op.drop_index(
        op.f("ix_support_conversations_coding_challenge_id"), table_name="support_conversations"
    )
    op.drop_index(op.f("ix_support_conversations_category"), table_name="support_conversations")
    op.drop_table("support_conversations")
    op.drop_table("users")
    op.drop_index(op.f("ix_coding_challenges_challenge_id"), table_name="coding_challenges")
    op.drop_index(op.f("ix_coding_challenges_category"), table_name="coding_challenges")
    op.drop_table("coding_challenges")
    op.execute("DROP TYPE difficulty")
