from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Response
from sqlalchemy.orm import Session

from app.api.v1.schemas.query_task import (
    DirectedQueryTaskCreateRequest,
    ErrorResponse,
    OneClickQueryTaskCreateRequest,
    QueryTaskCreateAcceptedResponse,
    QueryTaskCreateCacheHitResponse,
)
from app.common.response import build_error_response, build_success_response
from app.db.deps import get_db
from app.integrations.worker_client import enqueue_query_task_pipeline
from app.services.query_task_service import create_query_task_from_db, create_query_task_response

router = APIRouter(tags=["QueryTasks"])


@router.post(
    "/query-tasks",
    response_model=QueryTaskCreateCacheHitResponse | QueryTaskCreateAcceptedResponse | ErrorResponse,
)
def create_query_task(
    response: Response,
    payload: Annotated[OneClickQueryTaskCreateRequest | DirectedQueryTaskCreateRequest, Body()],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    try:
        status_code, result = create_query_task_from_db(db, payload.model_dump())
    except Exception:
        status_code, result = create_query_task_response(payload.model_dump())
    response.status_code = status_code

    if status_code == 422 and result["error"]:
        return build_error_response(
            code=result["error"]["code"],
            message=result["error"]["message"],
            details=result["error"]["details"],
        )

    if status_code == 202 and result["data"]:
        enqueue_query_task_pipeline(result["data"]["query_task_id"])

    return build_success_response(
        data=result["data"],
        meta=result["meta"],
    )
