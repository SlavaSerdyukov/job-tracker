from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.application_event import ApplicationEventType
from app.models.user import User
from app.schemas.application_event import ApplicationEventOut
from app.schemas.application_note import ApplicationNoteCreate
from app.services.application_event_service import (
    create_event,
    get_application_timeline,
)
from app.services.application_service import get_application_by_id

router = APIRouter(
    prefix="/applications/{app_id}",
    tags=["applications-timeline"],
)


@router.get("/timeline", response_model=list[ApplicationEventOut])
def application_timeline(
    app_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    application = get_application_by_id(db=db, user_id=user.id, app_id=app_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return get_application_timeline(
        db=db,
        user_id=user.id,
        application_id=app_id,
    )


@router.post("/notes", response_model=ApplicationEventOut, status_code=201)
def create_application_note(
    app_id: int,
    payload: ApplicationNoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    application = get_application_by_id(db=db, user_id=user.id, app_id=app_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    event = create_event(
        db=db,
        user_id=application.user_id,
        application_id=application.id,
        event_type=ApplicationEventType.note,
        note=payload.note,
    )

    db.commit()
    db.refresh(event)
    return event
