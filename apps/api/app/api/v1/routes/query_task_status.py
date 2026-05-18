from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.schemas.query_task import QueryTaskStatusResponse
from app.common.response import build_success_response
from app.db.deps import get_db
from app.services.query_task_service import (
    get_demo_query_task_status_response,
    get_query_task_status_from_db,
)

router = APIRouter(tags=["QueryTasks"])


@router.get("/query-tasks/{query_task_id}", response_model=QueryTaskStatusResponse)
def get_query_task_status(
    query_task_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    payload = get_query_task_status_from_db(db, query_task_id)
    if payload is None:
        payload = get_demo_query_task_status_response(query_task_id)
        if payload is None:
            raise HTTPException(status_code=404, detail="query task not found")

    data = {
        **payload["data"],
        "query_task_id": query_task_id,
    }

    response_payload = build_success_response(
        data=data,
        meta=payload["meta"],
    ) if payload["error"] is None else {
        **build_success_response(data=data, meta=payload["meta"]),
        "error": payload["error"],
    }
    return QueryTaskStatusResponse.model_validate(response_payload).model_dump()
