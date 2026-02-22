from datetime import datetime

from pydantic import BaseModel

from app.models.application import ApplicationStatus


class StatusCountOut(BaseModel):
    status: ApplicationStatus
    count: int


class ApplicationsSummaryOut(BaseModel):
    total: int
    by_status: list[StatusCountOut]


class TimeToStatusMetricOut(BaseModel):
    status: ApplicationStatus
    avg_days: float | None


class TimeToStatusOut(BaseModel):
    metrics: list[TimeToStatusMetricOut]


class StatusDurationMetricOut(BaseModel):
    status: ApplicationStatus
    avg_days: float | None


class StatusDurationOut(BaseModel):
    metrics: list[StatusDurationMetricOut]


class FunnelStepOut(BaseModel):
    step: ApplicationStatus
    count: int


class ApplicationsFunnelOut(BaseModel):
    steps: list[FunnelStepOut]


class RecruiterPerformanceItemOut(BaseModel):
    recruiter_email: str
    count: int


class RecruiterPerformanceOut(BaseModel):
    recruiters: list[RecruiterPerformanceItemOut]


class RecruiterPerformanceV2ItemOut(BaseModel):
    recruiter_email: str
    total: int
    by_status: list[StatusCountOut]
    last_contacted_at: datetime | None


class RecruiterPerformanceV2Out(BaseModel):
    recruiters: list[RecruiterPerformanceV2ItemOut]
