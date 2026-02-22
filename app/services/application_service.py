from datetime import datetime, timedelta, timezone

from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.application_event import ApplicationEventType
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.services.application_event_service import create_application_event

STATUS_FLOW_ORDER = [
    ApplicationStatus.applied,
    ApplicationStatus.screening,
    ApplicationStatus.interview,
    ApplicationStatus.offer,
    ApplicationStatus.accepted,
]
APPLICATION_UNIQUE_CONSTRAINT = "uq_user_company_position"
APPLICATION_CONFLICT_FIELDS = ["company_name", "position"]


def apply_status_flow(
    current: ApplicationStatus,
    new: ApplicationStatus,
) -> ApplicationStatus:
    if new == ApplicationStatus.rejected:
        return new

    if current == ApplicationStatus.rejected:
        raise ValueError("Invalid status transition")

    if current not in STATUS_FLOW_ORDER or new not in STATUS_FLOW_ORDER:
        raise ValueError("Invalid status transition")

    current_index = STATUS_FLOW_ORDER.index(current)
    new_index = STATUS_FLOW_ORDER.index(new)

    if new_index == current_index or new_index == current_index + 1:
        return new

    raise ValueError("Invalid status transition")


def get_application_conflict_detail(
    error: IntegrityError,
) -> dict[str, str | list[str]] | None:
    original_error = getattr(error, "orig", None)
    if original_error is None:
        return None

    message = str(original_error).lower()
    if APPLICATION_UNIQUE_CONSTRAINT in message:
        return {
            "message": "Application already exists for this user",
            "conflicting_fields": APPLICATION_CONFLICT_FIELDS,
        }

    if (
        "applications.user_id" in message
        and "applications.company_name" in message
        and "applications.position" in message
    ):
        return {
            "message": "Application already exists for this user",
            "conflicting_fields": APPLICATION_CONFLICT_FIELDS,
        }

    return None


def create_application(
    *,
    db: Session,
    user_id: int,
    payload: ApplicationCreate,
) -> Application:
    application = Application(user_id=user_id, **payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def get_application_by_id(
    *,
    db: Session,
    user_id: int,
    app_id: int,
) -> Application | None:
    stmt = select(Application).where(
        Application.id == app_id,
        Application.user_id == user_id,
    )
    return db.scalar(stmt)


def delete_application(*, db: Session, application: Application) -> None:
    db.delete(application)
    db.commit()


def _apply_filters(
    *,
    stmt: Select[tuple[Application]],
    user_id: int,
    status: ApplicationStatus | None,
    company: str | None,
    q: str | None,
) -> Select[tuple[Application]]:
    stmt = stmt.where(Application.user_id == user_id)

    if status is not None:
        stmt = stmt.where(Application.status == status)

    if company:
        stmt = stmt.where(Application.company_name.ilike(f"%{company}%"))

    if q:
        stmt = stmt.where(
            or_(
                Application.company_name.ilike(f"%{q}%"),
                Application.position.ilike(f"%{q}%"),
                Application.recruiter_email.ilike(f"%{q}%"),
            )
        )

    return stmt


def get_user_applications(
    *,
    db: Session,
    user_id: int,
    status: ApplicationStatus | None = None,
    company: str | None = None,
    q: str | None = None,
    sort: str = "-created_at",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Application], int]:
    base_stmt = _apply_filters(
        stmt=select(Application),
        user_id=user_id,
        status=status,
        company=company,
        q=q,
    )

    total_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = db.scalar(total_stmt) or 0

    descending = sort.startswith("-")
    field_name = sort[1:] if descending else sort

    if hasattr(Application, field_name):
        order_column = getattr(Application, field_name)
        base_stmt = base_stmt.order_by(
            order_column.desc() if descending else order_column.asc()
        )
    else:
        base_stmt = base_stmt.order_by(Application.created_at.desc())

    stmt = base_stmt.offset((page - 1) * page_size).limit(page_size)
    items = list(db.scalars(stmt).all())
    return items, total


def get_due_followups(
    *,
    db: Session,
    user_id: int,
    days: int = 3,
) -> list[Application]:
    deadline = datetime.now(timezone.utc) + timedelta(days=days)

    stmt = (
        select(Application)
        .where(
            Application.user_id == user_id,
            Application.follow_up_at.is_not(None),
            Application.follow_up_at <= deadline,
        )
        .order_by(Application.follow_up_at.asc())
    )

    return list(db.scalars(stmt).all())


def update_application(
    *,
    db: Session,
    user_id: int,
    application: Application,
    payload: ApplicationUpdate,
) -> Application:
    data = payload.model_dump(exclude_unset=True)

    old_status = application.status
    old_follow_up_at = application.follow_up_at
    old_recruiter_email = application.recruiter_email
    old_recruiter_name = application.recruiter_name

    if "status" in data:
        data["status"] = apply_status_flow(application.status, data["status"])
        if data["status"] != old_status:
            data["status_updated_at"] = datetime.now(timezone.utc)

    for key, value in data.items():
        setattr(application, key, value)

    if "status" in data and data["status"] != old_status:
        create_application_event(
            db=db,
            user_id=user_id,
            application_id=application.id,
            event_type=ApplicationEventType.status_change,
            from_status=old_status,
            to_status=data["status"],
        )

    if "follow_up_at" in data and data["follow_up_at"] != old_follow_up_at:
        create_application_event(
            db=db,
            user_id=user_id,
            application_id=application.id,
            event_type=ApplicationEventType.follow_up,
        )

    recruiter_email_changed = (
        "recruiter_email" in data
        and data["recruiter_email"] != old_recruiter_email
    )
    recruiter_name_changed = (
        "recruiter_name" in data
        and data["recruiter_name"] != old_recruiter_name
    )
    if recruiter_email_changed or recruiter_name_changed:
        create_application_event(
            db=db,
            user_id=user_id,
            application_id=application.id,
            event_type=ApplicationEventType.contact,
        )

    db.commit()
    db.refresh(application)
    return application
