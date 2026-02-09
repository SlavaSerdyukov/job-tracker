from pydantic import BaseModel


class ApplicationsStatsOut(BaseModel):
    total: int
    statuses: dict[str, int]
