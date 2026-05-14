from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.result_snapshot import ResultSnapshot


def get_result_snapshot_by_id(db: Session, result_snapshot_id: UUID) -> ResultSnapshot | None:
    return db.get(ResultSnapshot, result_snapshot_id)
