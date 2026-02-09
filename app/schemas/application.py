from datetime import datetime

from pydantic import BaseModel

from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    company_name: str
    position: str
    status: ApplicationStatus = ApplicationStatus.applied


class ApplicationUpdate(BaseModel):
    company_name: str | None = None
    position: str | None = None
    status: ApplicationStatus | None = None


class ApplicationOut(BaseModel):
    id: int
    company_name: str
    position: str
    status: ApplicationStatus
    created_at: datetime

    class Config:
        from_attributes = True
