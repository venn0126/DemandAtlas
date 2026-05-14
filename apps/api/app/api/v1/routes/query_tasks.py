from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Response

from app.api.v1.schemas.query_task import (
    DirectedQueryTaskCreateRequest,
    ErrorResponse,
    OneClickQueryTaskCreateRequest,
    QueryTaskCreateAcceptedResponse,
    QueryTaskCreateCacheHitResponse,
)
from app.common.response import build_error_response, build_success_response
from app.services.query_task_service import create_query_task_response

router = APIRouter(tags=["QueryTasks"])


@router.post(
    "/query-tasks",
    response_model=QueryTaskCreateCacheHitResponse | QueryTaskCreateAcceptedResponse | ErrorResponse,
)
def create_query_task(
    response: Response,
    payload: Annotated[OneClickQueryTaskCreateRequest | DirectedQueryTaskCreateRequest, Body()],
) -> dict:
    status_code, result = create_query_task_response(payload.model_dump())
    response.status_code = status_code

    if status_code == 422 and result["error"]:
        return build_error_response(
            code=result["error"]["code"],
            message=result["error"]["message"],
            details=result["error"]["details"],
        )

    return build_success_response(
        data=result["data"],
        meta=result["meta"],
    )
