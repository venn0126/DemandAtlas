from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.schemas.query_task import QueryTaskStatusResponse
from app.common.response import build_success_response
from app.db.deps import get_db
from app.services.query_task_service import (
    get_query_task_status_from_db,
    get_query_task_status_response,
)

router = APIRouter(tags=["QueryTasks"])


@router.get("/query-tasks/{query_task_id}", response_model=QueryTaskStatusResponse)
def get_query_task_status(
    query_task_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    status_map = {
        "qt_pending": "pending",
        "qt_running": "running",
        "qt_partial": "partial_success",
        "qt_success": "success",
        "qt_failed": "failed",
    }

    payload = get_query_task_status_from_db(db, query_task_id)
    if payload is None:
        scenario = status_map.get(query_task_id)
        if scenario is None:
            raise HTTPException(status_code=404, detail="query task not found")
        payload = get_query_task_status_response(scenario)

    data = {
        **payload["data"],
        "query_task_id": query_task_id,
    }

    return build_success_response(
        data=data,
        meta=payload["meta"],
    ) if payload["error"] is None else {
        **build_success_response(data=data, meta=payload["meta"]),
        "error": payload["error"],
    }
