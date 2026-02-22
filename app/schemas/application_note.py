from pydantic import BaseModel


class ApplicationNoteCreate(BaseModel):
    note: str
