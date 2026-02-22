"""phase2 application fields and events

Revision ID: a4e9f4c6d2b1
Revises: 07c3b8e0b446
Create Date: 2026-02-17 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "a4e9f4c6d2b1"
down_revision: str | Sequence[str] | None = "07c3b8e0b446"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


EVENT_TYPE_ENUM = postgresql.ENUM(
    "status_change",
    "follow_up",
    "note",
    "contact",
    name="applicationeventtype",
    create_type=False,
)

APPLICATION_STATUS_ENUM = postgresql.ENUM(
    "applied",
    "screening",
    "interview",
    "offer",
    "accepted",
    "rejected",
    name="applicationstatus",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    cols = {c["name"] for c in inspector.get_columns("applications")}

    def add_col(name: str, column: sa.Column):
        if name not in cols:
            op.add_column("applications", column)

    add_col("recruiter_email", sa.Column("recruiter_email", sa.String(255)))
    add_col("recruiter_name", sa.Column("recruiter_name", sa.String(255)))
    add_col("job_url", sa.Column("job_url", sa.String(500)))
    add_col("salary_range", sa.Column("salary_range", sa.String(255)))
    add_col("location", sa.Column("location", sa.String(255)))
    add_col(
        "follow_up_at",
        sa.Column("follow_up_at", sa.DateTime(timezone=True)),
    )
    add_col(
        "status_updated_at",
        sa.Column("status_updated_at", sa.DateTime(timezone=True)),
    )

    existing_indexes = {
        i["name"] for i in inspector.get_indexes("applications")
    }

    if "ix_applications_follow_up_at" not in existing_indexes:
        op.create_index(
            "ix_applications_follow_up_at",
            "applications",
            ["follow_up_at"],
        )

    if "ix_applications_status_updated_at" not in existing_indexes:
        op.create_index(
            "ix_applications_status_updated_at",
            "applications",
            ["status_updated_at"],
        )

    if bind.dialect.name == "postgresql":
        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_type
                    WHERE typname = 'applicationeventtype'
                ) THEN
                    CREATE TYPE applicationeventtype AS ENUM (
                        'status_change',
                        'follow_up',
                        'note',
                        'contact'
                    );
                END IF;
            END$$;
            """
        )

        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'applicationstatus'
                ) THEN
                    CREATE TYPE applicationstatus AS ENUM (
                        'applied',
                        'screening',
                        'interview',
                        'offer',
                        'accepted',
                        'rejected'
                    );
                END IF;
            END$$;
            """
        )

    table_names = set(inspector.get_table_names())
    if "application_events" not in table_names:
        op.create_table(
            "application_events",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("application_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("event_type", EVENT_TYPE_ENUM, nullable=False),
            sa.Column("from_status", APPLICATION_STATUS_ENUM, nullable=True),
            sa.Column("to_status", APPLICATION_STATUS_ENUM, nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["application_id"],
                ["applications.id"],
                ondelete="CASCADE",
            ),
            sa.ForeignKeyConstraint(
                ["user_id"],
                ["users.id"],
                ondelete="CASCADE",
            ),
        )

    refreshed_tables = set(sa.inspect(bind).get_table_names())
    event_indexes = (
        {i["name"] for i in inspector.get_indexes("application_events")}
        if "application_events" in refreshed_tables
        else set()
    )
    if "ix_application_events_application_id" not in event_indexes:
        op.create_index(
            "ix_application_events_application_id",
            "application_events",
            ["application_id"],
        )
    if "ix_application_events_user_id" not in event_indexes:
        op.create_index(
            "ix_application_events_user_id",
            "application_events",
            ["user_id"],
        )
    if "ix_application_events_event_type" not in event_indexes:
        op.create_index(
            "ix_application_events_event_type",
            "application_events",
            ["event_type"],
        )
    if "ix_application_events_created_at" not in event_indexes:
        op.create_index(
            "ix_application_events_created_at",
            "application_events",
            ["created_at"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "application_events" in inspector.get_table_names():
        existing_event_indexes = {
            i["name"] for i in inspector.get_indexes("application_events")
        }
        if "ix_application_events_created_at" in existing_event_indexes:
            op.drop_index(
                "ix_application_events_created_at",
                table_name="application_events",
            )
        if "ix_application_events_event_type" in existing_event_indexes:
            op.drop_index(
                "ix_application_events_event_type",
                table_name="application_events",
            )
        if "ix_application_events_user_id" in existing_event_indexes:
            op.drop_index(
                "ix_application_events_user_id",
                table_name="application_events",
            )
        if "ix_application_events_application_id" in existing_event_indexes:
            op.drop_index(
                "ix_application_events_application_id",
                table_name="application_events",
            )
        op.drop_table("application_events")

    cols = {c["name"] for c in inspector.get_columns("applications")}

    for col in [
        "status_updated_at",
        "follow_up_at",
        "location",
        "salary_range",
        "job_url",
        "recruiter_name",
        "recruiter_email",
    ]:
        if col in cols:
            op.drop_column("applications", col)
