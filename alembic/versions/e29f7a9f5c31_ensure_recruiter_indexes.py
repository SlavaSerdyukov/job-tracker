"""ensure recruiter indexes

Revision ID: e29f7a9f5c31
Revises: a4e9f4c6d2b1
Create Date: 2026-02-22 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e29f7a9f5c31"
down_revision: str | Sequence[str] | None = "a4e9f4c6d2b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "applications" not in inspector.get_table_names():
        return

    columns = {
        column["name"] for column in inspector.get_columns("applications")
    }
    indexes = {
        index["name"] for index in inspector.get_indexes("applications")
    }

    if (
        "recruiter_email" in columns
        and "ix_applications_recruiter_email" not in indexes
    ):
        op.create_index(
            "ix_applications_recruiter_email",
            "applications",
            ["recruiter_email"],
        )

    if (
        "last_contacted_at" in columns
        and "ix_applications_last_contacted_at" not in indexes
    ):
        op.create_index(
            "ix_applications_last_contacted_at",
            "applications",
            ["last_contacted_at"],
        )


def downgrade() -> None:
    return
