import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ApplicationStatus(enum.StrEnum):
    applied = "applied"
    screening = "screening"
    interview = "interview"
    offer = "offer"
    accepted = "accepted"
    rejected = "rejected"


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "company_name",
            "position",
            name="uq_user_company_position",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    company_name: Mapped[str] = mapped_column(String(255), index=True)
    position: Mapped[str] = mapped_column(String(255))

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus),
        default=ApplicationStatus.applied,
        index=True,
    )

    recruiter_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    recruiter_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    job_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    salary_range: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    follow_up_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    status_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user = relationship("User")
    events = relationship(
        "ApplicationEvent",
        back_populates="application",
        cascade="all, delete-orphan",
    )
