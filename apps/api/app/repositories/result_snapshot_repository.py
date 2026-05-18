from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.result_snapshot import ResultSnapshot


def get_result_snapshot_by_id(db: Session, result_snapshot_id: UUID) -> ResultSnapshot | None:
    stmt = (
        select(ResultSnapshot)
        .options(selectinload(ResultSnapshot.query_task))
        .where(ResultSnapshot.id == result_snapshot_id)
    )
    return db.scalar(stmt)
