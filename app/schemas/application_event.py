from datetime import datetime

from pydantic import BaseModel

from app.models.application import ApplicationStatus
from app.models.application_event import ApplicationEventType


class ApplicationEventOut(BaseModel):
    id: int
    application_id: int
    event_type: ApplicationEventType
    from_status: ApplicationStatus | None
    to_status: ApplicationStatus | None
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
