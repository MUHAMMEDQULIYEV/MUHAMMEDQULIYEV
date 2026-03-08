"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("preferences", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    # tasks table
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "category",
            sa.Enum("work", "study", "learning", "personal", name="taskcategory"),
            nullable=False,
        ),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "priority",
            sa.Enum("high", "medium", "low", name="taskpriority"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("not_started", "in_progress", "completed", "archived", name="taskstatus"),
            nullable=False,
        ),
        sa.Column("estimated_duration", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # notes table
    op.create_table(
        "notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # flashcard_decks table
    op.create_table(
        "flashcard_decks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "language",
            sa.Enum("english", "korean", name="decklanguage"),
            nullable=False,
        ),
        sa.Column(
            "source_type",
            sa.Enum("youtube", "manual", "upload", name="decksourcetype"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # flashcards table
    op.create_table(
        "flashcards",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deck_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("front", sa.String(length=1000), nullable=False),
        sa.Column("back", sa.String(length=1000), nullable=False),
        sa.Column("ease_factor", sa.Float(), nullable=True),
        sa.Column("interval", sa.Integer(), nullable=True),
        sa.Column("repetitions", sa.Integer(), nullable=True),
        sa.Column("last_reviewed", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_review", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["deck_id"], ["flashcard_decks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # language_vocabulary table
    op.create_table(
        "language_vocabulary",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("word", sa.String(length=255), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=False),
        sa.Column("translation", sa.String(length=500), nullable=True),
        sa.Column("frequency_count", sa.Integer(), nullable=True),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("learned", sa.Boolean(), nullable=True),
        sa.Column("date_learned", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pos", sa.String(length=50), nullable=True),
        sa.Column("difficulty", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # productivity_analytics table
    op.create_table(
        "productivity_analytics",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("tasks_completed", sa.Integer(), nullable=True),
        sa.Column("tasks_total", sa.Integer(), nullable=True),
        sa.Column("category_breakdown", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("time_spent", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("completion_rate", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # language_progress table
    op.create_table(
        "language_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("words_learned", sa.Integer(), nullable=True),
        sa.Column("flashcard_accuracy", sa.Float(), nullable=True),
        sa.Column("time_spent", sa.Integer(), nullable=True),
        sa.Column("topics_studied", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("language_progress")
    op.drop_table("productivity_analytics")
    op.drop_table("language_vocabulary")
    op.drop_table("flashcards")
    op.drop_table("flashcard_decks")
    op.drop_table("notes")
    op.drop_table("tasks")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    # Drop enums
    sa.Enum(name="taskcategory").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="taskpriority").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="taskstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="decklanguage").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="decksourcetype").drop(op.get_bind(), checkfirst=True)
