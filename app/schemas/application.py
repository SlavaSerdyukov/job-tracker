from datetime import datetime

from pydantic import BaseModel

from app.models.application import ApplicationStatus


class ApplicationBase(BaseModel):
    company_name: str
    position: str
    recruiter_name: str | None = None
    recruiter_email: str | None = None
    job_url: str | None = None
    salary_range: str | None = None
    location: str | None = None
    follow_up_at: datetime | None = None


class ApplicationCreate(ApplicationBase):
    status: ApplicationStatus = ApplicationStatus.applied


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    recruiter_name: str | None = None
    recruiter_email: str | None = None
    job_url: str | None = None
    salary_range: str | None = None
    location: str | None = None
    follow_up_at: datetime | None = None


class ApplicationOut(ApplicationBase):
    id: int
    status: ApplicationStatus
    status_updated_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedApplications(BaseModel):
    items: list[ApplicationOut]
    total: int
    page: int
    page_size: int
