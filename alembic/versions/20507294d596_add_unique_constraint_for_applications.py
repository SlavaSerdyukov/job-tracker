"""add unique constraint for applications

Revision ID: 20507294d596
Revises: 6c559809ae70
Create Date: 2026-02-08 16:28:08.553400

"""

from collections.abc import Sequence

revision: str = "20507294d596"
down_revision: str | Sequence[str] | None = "6c559809ae70"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
