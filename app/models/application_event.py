import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.application import ApplicationStatus
from app.models.base import Base


class ApplicationEventType(enum.StrEnum):
    status_change = "status_change"
    follow_up = "follow_up"
    note = "note"
    contact = "contact"


class ApplicationEvent(Base):
    __tablename__ = "application_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    event_type: Mapped[ApplicationEventType] = mapped_column(
        Enum(
            ApplicationEventType,
            name="applicationeventtype",
            create_type=False,
        ),
        index=True,
    )
    from_status: Mapped[ApplicationStatus | None] = mapped_column(
        Enum(ApplicationStatus, name="applicationstatus", create_type=False),
        nullable=True,
    )
    to_status: Mapped[ApplicationStatus | None] = mapped_column(
        Enum(ApplicationStatus, name="applicationstatus", create_type=False),
        nullable=True,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    application = relationship("Application", back_populates="events")
    user = relationship("User")
