from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.schemas.result_snapshot import (
    ResultSnapshotSummary,
    ResultSnapshotSummaryResponse,
)
from app.api.v1.schemas.result_snapshot_explore import (
    BoardListData,
    BoardListResponse,
    ClusterDetailResponse,
    DemandClusterDetail,
)
from app.common.response import build_success_response
from app.db.deps import get_db
from app.services.result_snapshot_explore_service import (
    get_cluster_detail_from_db,
    get_demo_cluster_detail,
    get_demo_result_snapshot_board,
    get_result_snapshot_board_from_db,
)
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


@router.get(
    "/result-snapshots/{result_snapshot_id}/boards/{board_type}",
    response_model=BoardListResponse,
)
def get_result_snapshot_board(
    result_snapshot_id: str,
    board_type: str,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    payload = get_result_snapshot_board_from_db(db, result_snapshot_id, board_type)

    if payload is None:
        payload = get_demo_result_snapshot_board(result_snapshot_id, board_type)

    if not payload:
        raise HTTPException(status_code=404, detail="result snapshot board not found")

    response_payload = build_success_response(
        data=BoardListData.model_validate(payload["data"]).model_dump(),
        meta=payload["meta"],
    )
    return BoardListResponse.model_validate(response_payload).model_dump()


@router.get(
    "/result-snapshots/{result_snapshot_id}/clusters/{cluster_id}",
    response_model=ClusterDetailResponse,
)
def get_cluster_detail(
    result_snapshot_id: str,
    cluster_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    payload = get_cluster_detail_from_db(db, result_snapshot_id, cluster_id)

    if payload is None:
        payload = get_demo_cluster_detail(result_snapshot_id, cluster_id)

    if not payload:
        raise HTTPException(status_code=404, detail="cluster detail not found")

    response_payload = build_success_response(
        data=DemandClusterDetail.model_validate(payload["data"]).model_dump(),
        meta=payload["meta"],
    )
    return ClusterDetailResponse.model_validate(response_payload).model_dump()
