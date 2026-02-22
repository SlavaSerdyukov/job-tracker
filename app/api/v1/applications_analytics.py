from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import (
    ApplicationsFunnelOut,
    ApplicationsSummaryOut,
    RecruiterPerformanceOut,
    RecruiterPerformanceV2Out,
    TimeToStatusOut,
)
from app.services.application_analytics_service import (
    get_applications_summary,
    get_funnel,
    get_recruiter_performance,
    get_recruiter_performance_v2,
    get_time_to_status,
)

router = APIRouter(
    prefix="/applications/analytics",
    tags=["applications-analytics"],
)


@router.get("/summary", response_model=ApplicationsSummaryOut)
def applications_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_applications_summary(db=db, user_id=user.id)


@router.get("/time-to-status", response_model=TimeToStatusOut)
def applications_time_to_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_time_to_status(db=db, user_id=user.id)


@router.get("/funnel", response_model=ApplicationsFunnelOut)
def applications_funnel(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_funnel(db=db, user_id=user.id)


@router.get("/recruiter-performance", response_model=RecruiterPerformanceOut)
def applications_recruiter_performance(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_recruiter_performance(db=db, user_id=user.id)


@router.get(
    "/recruiter-performance-v2",
    response_model=RecruiterPerformanceV2Out,
)
def applications_recruiter_performance_v2(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_recruiter_performance_v2(db=db, user_id=user.id)
