from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.application_event import ApplicationEvent, ApplicationEventType


def create_event(
    *,
    db: Session,
    user_id: int,
    application_id: int,
    event_type: ApplicationEventType,
    from_status: ApplicationStatus | None = None,
    to_status: ApplicationStatus | None = None,
    note: str | None = None,
) -> ApplicationEvent:
    if event_type == ApplicationEventType.follow_up:
        application = db.get(Application, application_id)
        if application is None or application.follow_up_at is None:
            return None
        if note is None:
            note = "Follow-up scheduled"

    event = ApplicationEvent(
        user_id=user_id,
        application_id=application_id,
        event_type=event_type,
        from_status=from_status,
        to_status=to_status,
        note=note,
    )

    db.add(event)
    return event


def get_application_timeline(
    *,
    db: Session,
    user_id: int,
    application_id: int,
) -> list[ApplicationEvent]:
    stmt = (
        select(ApplicationEvent)
        .where(
            ApplicationEvent.user_id == user_id,
            ApplicationEvent.application_id == application_id,
        )
        .order_by(
            ApplicationEvent.created_at.desc(),
            ApplicationEvent.id.desc(),
        )
    )
    return list(db.scalars(stmt).all())


create_application_event = create_event
