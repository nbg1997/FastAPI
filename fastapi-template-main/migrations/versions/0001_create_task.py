"""Создать таблицу задач.

Revision ID: 0001
Revises: None
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("done", sa.Boolean(), nullable=False),
        sa.CheckConstraint("length(title) BETWEEN 1 AND 120", name="task_title_length"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("task")
