"""add recruiter and status tracking

Revision ID: 07c3b8e0b446
Revises: 20507294d596
Create Date: 2026-02-11 16:53:47.212743
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "07c3b8e0b446"
down_revision: str | None = "20507294d596"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "applications",
        sa.Column("recruiter_email", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "applications",
        sa.Column("status_updated_at", sa.DateTime(
            timezone=True), nullable=True),
    )

    op.create_index(
        "ix_applications_recruiter_email",
        "applications",
        ["recruiter_email"],
    )


def downgrade() -> None:
    op.drop_index("ix_applications_recruiter_email", table_name="applications")

    op.drop_column("applications", "status_updated_at")
    op.drop_column("applications", "recruiter_email")
