from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.application_event import ApplicationEvent, ApplicationEventType

FUNNEL_STEPS = [
    ApplicationStatus.applied,
    ApplicationStatus.screening,
    ApplicationStatus.interview,
    ApplicationStatus.offer,
    ApplicationStatus.accepted,
]


def get_applications_summary(*, db: Session, user_id: int) -> dict:
    stmt = (
        select(Application.status, func.count(Application.id))
        .where(Application.user_id == user_id)
        .group_by(Application.status)
    )
    rows = db.execute(stmt).all()

    counts_by_status = {status: count for status, count in rows}

    return {
        "total": sum(counts_by_status.values()),
        "by_status": [
            {
                "status": status,
                "count": counts_by_status.get(status, 0),
            }
            for status in ApplicationStatus
        ],
    }


def get_time_to_status(*, db: Session, user_id: int) -> dict:
    duration_days = (
        func.extract(
            "epoch",
            Application.status_updated_at - Application.created_at,
        )
        / 86400.0
    )

    stmt = (
        select(Application.status, func.avg(duration_days))
        .where(
            Application.user_id == user_id,
            Application.status_updated_at.is_not(None),
        )
        .group_by(Application.status)
    )
    rows = db.execute(stmt).all()

    avg_days_by_status = {
        status: float(avg_days) if avg_days is not None else None
        for status, avg_days in rows
    }

    return {
        "metrics": [
            {
                "status": status,
                "avg_days": avg_days_by_status.get(status),
            }
            for status in ApplicationStatus
        ]
    }


def get_status_duration_metrics(*, db: Session, user_id: int) -> dict:
    stmt = (
        select(
            ApplicationEvent.application_id,
            ApplicationEvent.to_status,
            ApplicationEvent.created_at,
        )
        .where(
            ApplicationEvent.user_id == user_id,
            ApplicationEvent.event_type == ApplicationEventType.status_change,
            ApplicationEvent.to_status.is_not(None),
        )
        .order_by(
            ApplicationEvent.application_id.asc(),
            ApplicationEvent.created_at.asc(),
            ApplicationEvent.id.asc(),
        )
    )
    rows = db.execute(stmt).all()

    durations_by_status: dict[ApplicationStatus, list[float]] = {
        status: []
        for status in ApplicationStatus
    }
    last_by_application: dict[int, tuple[ApplicationStatus, datetime]] = {}

    for application_id, to_status, created_at in rows:
        if application_id in last_by_application:
            prev_status, prev_created_at = last_by_application[application_id]
            delta_days = (
                created_at - prev_created_at
            ).total_seconds() / 86400.0
            if delta_days >= 0:
                durations_by_status[prev_status].append(delta_days)
        last_by_application[application_id] = (to_status, created_at)

    return {
        "metrics": [
            {
                "status": status,
                "avg_days": (
                    sum(durations_by_status[status])
                    / len(durations_by_status[status])
                    if durations_by_status[status]
                    else None
                ),
            }
            for status in ApplicationStatus
        ]
    }


def get_funnel(*, db: Session, user_id: int) -> dict:
    stmt = (
        select(Application.status, func.count(Application.id))
        .where(
            Application.user_id == user_id,
            Application.status.in_(FUNNEL_STEPS),
        )
        .group_by(Application.status)
    )
    rows = db.execute(stmt).all()

    exact_counts = {status: count for status, count in rows}

    cumulative: dict[ApplicationStatus, int] = {}
    running_total = 0
    for status in reversed(FUNNEL_STEPS):
        running_total += exact_counts.get(status, 0)
        cumulative[status] = running_total

    return {
        "steps": [
            {
                "step": status,
                "count": cumulative.get(status, 0),
            }
            for status in FUNNEL_STEPS
        ]
    }


def get_recruiter_performance(*, db: Session, user_id: int) -> dict:
    normalized_email = func.lower(func.trim(Application.recruiter_email))

    stmt = (
        select(
            normalized_email.label("recruiter_email"),
            func.count(Application.id).label("count"),
        )
        .where(
            Application.user_id == user_id,
            Application.recruiter_email.is_not(None),
            func.length(func.trim(Application.recruiter_email)) > 0,
        )
        .group_by(normalized_email)
        .order_by(func.count(Application.id).desc(), normalized_email.asc())
    )
    rows = db.execute(stmt).all()

    return {
        "recruiters": [
            {
                "recruiter_email": recruiter_email,
                "count": count,
            }
            for recruiter_email, count in rows
        ]
    }


def get_recruiter_performance_v2(*, db: Session, user_id: int) -> dict:
    normalized_email = func.lower(func.trim(Application.recruiter_email))
    filters = (
        Application.user_id == user_id,
        Application.recruiter_email.is_not(None),
        func.length(func.trim(Application.recruiter_email)) > 0,
    )

    status_stmt = (
        select(
            normalized_email.label("recruiter_email"),
            Application.status,
            func.count(Application.id).label("count"),
        )
        .where(*filters)
        .group_by(normalized_email, Application.status)
    )
    status_rows = db.execute(status_stmt).all()

    status_counts_by_recruiter: dict[str, dict[ApplicationStatus, int]] = {}
    for recruiter_email, status, count in status_rows:
        recruiter_counts = status_counts_by_recruiter.setdefault(
            recruiter_email,
            {},
        )
        recruiter_counts[status] = int(count)

    last_contacted_column = getattr(Application, "last_contacted_at", None)
    if last_contacted_column is not None:
        totals_stmt = (
            select(
                normalized_email.label("recruiter_email"),
                func.count(Application.id).label("total"),
                func.max(last_contacted_column).label("last_contacted_at"),
            )
            .where(*filters)
            .group_by(normalized_email)
            .order_by(
                func.count(Application.id).desc(),
                normalized_email.asc(),
            )
        )
        totals_rows = db.execute(totals_stmt).all()
        return {
            "recruiters": [
                {
                    "recruiter_email": recruiter_email,
                    "total": int(total),
                    "by_status": [
                        {
                            "status": status,
                            "count": status_counts_by_recruiter.get(
                                recruiter_email,
                                {},
                            ).get(status, 0),
                        }
                        for status in ApplicationStatus
                    ],
                    "last_contacted_at": last_contacted_at,
                }
                for recruiter_email, total, last_contacted_at in totals_rows
            ]
        }

    totals_stmt = (
        select(
            normalized_email.label("recruiter_email"),
            func.count(Application.id).label("total"),
        )
        .where(*filters)
        .group_by(normalized_email)
        .order_by(func.count(Application.id).desc(), normalized_email.asc())
    )
    totals_rows = db.execute(totals_stmt).all()

    return {
        "recruiters": [
            {
                "recruiter_email": recruiter_email,
                "total": int(total),
                "by_status": [
                    {
                        "status": status,
                        "count": status_counts_by_recruiter.get(
                            recruiter_email,
                            {},
                        ).get(status, 0),
                    }
                    for status in ApplicationStatus
                ],
                "last_contacted_at": None,
            }
            for recruiter_email, total in totals_rows
        ]
    }
