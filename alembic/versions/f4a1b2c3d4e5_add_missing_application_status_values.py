"""add missing application status values

Revision ID: f4a1b2c3d4e5
Revises: e29f7a9f5c31
Create Date: 2026-09-01 10:35:00.000000
"""

from collections.abc import Sequence

from alembic import op

revision: str = "f4a1b2c3d4e5"
down_revision: str | Sequence[str] | None = "e29f7a9f5c31"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'screening'")
    op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'accepted'")


def downgrade() -> None:
    # PostgreSQL does not support removing individual enum values safely.
    return
