from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.schemas.result_snapshot import (
    ResultSnapshotSummary,
    ResultSnapshotSummaryResponse,
)
from app.common.response import build_success_response
from app.db.deps import get_db
from app.services.result_snapshot_service import (
    get_demo_result_snapshot_summary,
    get_result_snapshot_summary_from_db,
)

router = APIRouter(tags=["ResultSnapshots"])


@router.get(
    "/result-snapshots/{result_snapshot_id}",
    response_model=ResultSnapshotSummaryResponse,
)
def get_result_snapshot(
    result_snapshot_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    payload = get_result_snapshot_summary_from_db(db, result_snapshot_id)

    if payload is None:
        payload = get_demo_result_snapshot_summary(result_snapshot_id)

    if not payload:
        raise HTTPException(status_code=404, detail="result snapshot not found")

    response_payload = build_success_response(
        data=ResultSnapshotSummary.model_validate(payload["data"]).model_dump(),
        meta=payload["meta"],
    )
    return ResultSnapshotSummaryResponse.model_validate(response_payload).model_dump()
