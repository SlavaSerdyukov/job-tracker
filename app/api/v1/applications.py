from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.application import ApplicationStatus
from app.models.user import User
from app.schemas.analytics import StatusDurationOut
from app.schemas.application import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationUpdate,
    PaginatedApplications,
)
from app.services.application_analytics_service import (
    get_status_duration_metrics,
)
from app.services.application_service import (
    create_application,
    delete_application,
    get_application_by_id,
    get_application_conflict_detail,
    get_due_followups,
    get_user_applications,
    update_application,
)

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application_endpoint(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return create_application(db=db, user_id=user.id, payload=payload)
    except IntegrityError as err:
        db.rollback()
        detail = get_application_conflict_detail(err)
        if detail is not None:
            raise HTTPException(status_code=409, detail=detail) from err
        raise HTTPException(
            status_code=409,
            detail="Application data conflict",
        ) from err


@router.get("", response_model=PaginatedApplications)
def list_applications(
    status: ApplicationStatus | None = Query(default=None),
    company: str | None = Query(default=None),
    q: str | None = Query(default=None),
    sort: str = Query(default="-created_at"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = get_user_applications(
        db=db,
        user_id=user.id,
        status=status,
        company=company,
        q=q,
        sort=sort,
        page=page,
        page_size=page_size,
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/followups", response_model=list[ApplicationOut])
def upcoming_followups(
    days: int = Query(default=3, ge=1, le=30),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_due_followups(db=db, user_id=user.id, days=days)


@router.get("/{app_id}", response_model=ApplicationOut)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    application = get_application_by_id(db=db, user_id=user.id, app_id=app_id)

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return application


@router.patch("/{app_id}", response_model=ApplicationOut)
def update_application_endpoint(
    app_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    application = get_application_by_id(db=db, user_id=user.id, app_id=app_id)

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    try:
        return update_application(
            db=db,
            user_id=user.id,
            application=application,
            payload=payload,
        )
    except IntegrityError as err:
        db.rollback()
        detail = get_application_conflict_detail(err)
        if detail is not None:
            raise HTTPException(status_code=409, detail=detail) from err
        raise HTTPException(
            status_code=409,
            detail="Application data conflict",
        ) from err
    except ValueError as err:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(err)) from err


@router.delete("/{app_id}", status_code=204)
def delete_application_endpoint(
    app_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    application = get_application_by_id(db=db, user_id=user.id, app_id=app_id)

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    delete_application(db=db, application=application)


@router.get("/analytics/status-duration", response_model=StatusDurationOut)
def application_status_duration_analytics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_status_duration_metrics(db=db, user_id=user.id)
