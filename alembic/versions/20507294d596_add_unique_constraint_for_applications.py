"""add unique constraint for applications

Revision ID: 20507294d596
Revises: 6c559809ae70
Create Date: 2026-02-08 16:28:08.553400

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20507294d596"
down_revision: str | Sequence[str] | None = "6c559809ae70"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_user_company_position",
        "applications",
        ["user_id", "company_name", "position"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_user_company_position",
        "applications",
        type_="unique",
    )
