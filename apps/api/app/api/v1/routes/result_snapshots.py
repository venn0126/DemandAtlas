from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.v1.schemas.result_snapshot import (
    ResultSnapshotSummary,
    ResultSnapshotSummaryResponse,
)
from app.common.response import build_success_response
from app.services.result_snapshot_service import get_result_snapshot_summary

router = APIRouter(tags=["ResultSnapshots"])


@router.get(
    "/result-snapshots/{result_snapshot_id}",
    response_model=ResultSnapshotSummaryResponse,
)
def get_result_snapshot(result_snapshot_id: str) -> dict:
    payload = get_result_snapshot_summary(result_snapshot_id)

    if not payload:
        raise HTTPException(status_code=404, detail="result snapshot not found")

    return build_success_response(
        data=ResultSnapshotSummary.model_validate(payload["data"]).model_dump(),
        meta=payload["meta"],
    )
