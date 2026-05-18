from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Response
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
from app.services.query_task_service import (
    create_query_task_from_db,
    mark_query_task_enqueue_failed,
)

router = APIRouter(tags=["QueryTasks"])
logger = logging.getLogger(__name__)


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
    except Exception as exc:
        logger.exception("create_query_task failed")
        raise HTTPException(status_code=500, detail="failed to create query task") from exc
    response.status_code = status_code

    if status_code == 422 and result["error"]:
        return build_error_response(
            code=result["error"]["code"],
            message=result["error"]["message"],
            details=result["error"]["details"],
        )

    if status_code == 202 and result["data"]:
        query_task_id = result["data"]["query_task_id"]
        cache_source = result["meta"].get("cache_source")
        if cache_source in {None, "cache_miss"}:
            if not enqueue_query_task_pipeline(query_task_id):
                logger.warning("query task enqueue failed, marking task as failed", extra={"query_task_id": query_task_id})
                mark_query_task_enqueue_failed(db, query_task_id)

    return build_success_response(
        data=result["data"],
        meta=result["meta"],
    )
