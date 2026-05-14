from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.schemas.query_task import QueryTaskStatusResponse
from app.common.response import build_success_response
from app.services.query_task_service import get_query_task_status_response

router = APIRouter(tags=["QueryTasks"])


@router.get("/query-tasks/{query_task_id}", response_model=QueryTaskStatusResponse)
def get_query_task_status(query_task_id: str) -> dict:
    status_map = {
        "qt_pending": "pending",
        "qt_running": "running",
        "qt_partial": "partial_success",
        "qt_success": "success",
        "qt_failed": "failed",
    }

    scenario = status_map.get(query_task_id, "running")
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
