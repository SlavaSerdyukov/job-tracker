from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from app.models.application import Application, ApplicationStatus
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationOut, ApplicationUpdate
from app.schemas.pagination import Page
from app.schemas.stats import ApplicationsStatsOut
from app.services.application_service import (
    apply_sort,
    build_user_applications_query,
    paginate,
)

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/stats", response_model=ApplicationsStatsOut)
def applications_stats(
    status: ApplicationStatus | None = Query(default=None),
    company: str | None = Query(default=None),
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base_query = build_user_applications_query(
        db=db,
        user_id=user.id,
        status=status,
        company=company,
        q=q,
    )

    rows = (
        base_query.order_by(None)
        .with_entities(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )

    statuses = {k.value: int(v) for k, v in rows if k is not None}
    total = sum(statuses.values())

    return {"total": total, "statuses": statuses}


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(
    request: Request,
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rate_limit(key=f"user:{user.id}:create_app", limit=30, window_seconds=60)

    application = Application(
        user_id=user.id,
        **payload.model_dump(),
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


@router.get("", response_model=Page[ApplicationOut])
def list_applications(
    status: ApplicationStatus | None = Query(default=None),
    company: str | None = Query(default=None),
    q: str | None = Query(default=None),
    sort: str = Query(default="-created_at"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    base_query = build_user_applications_query(
        db=db,
        user_id=user.id,
        status=status,
        company=company,
        q=q,
    )

    base_query = apply_sort(base_query, sort)
    items, total = paginate(base_query, page=page, page_size=page_size)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{app_id}", response_model=ApplicationOut)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == app_id,
            Application.user_id == user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


@router.patch("/{app_id}", response_model=ApplicationOut)
def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == app_id,
            Application.user_id == user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(application, key, value)

    db.commit()
    db.refresh(application)

    return application


@router.delete("/{app_id}", status_code=204)
def delete_application(
    app_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    application = (
        db.query(Application)
        .filter(
            Application.id == app_id,
            Application.user_id == user.id,
        )
        .first()
    )

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(application)
    db.commit()
