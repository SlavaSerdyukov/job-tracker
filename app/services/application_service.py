from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from app.models.application import Application, ApplicationStatus


SORT_FIELDS: set[str] = {
    "created_at",
    "updated_at",
    "company_name",
    "position",
    "status",
    "id",
}


def build_user_applications_query(
    *,
    db: Session,
    user_id: int,
    status: ApplicationStatus | None = None,
    company: str | None = None,
    q: str | None = None,
) -> Query:
    query = db.query(Application).filter(Application.user_id == user_id)

    if status is not None:
        query = query.filter(Application.status == status)

    if company:
        query = query.filter(Application.company_name.ilike(f"%{company}%"))

    if q:
        query = query.filter(
            or_(
                Application.company_name.ilike(f"%{q}%"),
                Application.position.ilike(f"%{q}%"),
            )
        )

    return query


def apply_sort(query: Query, sort: str) -> Query:
    desc = sort.startswith("-")
    field = sort[1:] if desc else sort

    if field not in SORT_FIELDS:
        return query.order_by(Application.created_at.desc())

    column = getattr(Application, field)

    return query.order_by(column.desc() if desc else column.asc())


def paginate(query: Query, *, page: int, page_size: int) -> tuple[list[Application], int]:
    total = query.order_by(None).count()

    items = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total
