from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.v1.schemas.topic_template import (
    TopicTemplateDetail,
    TopicTemplateDetailResponse,
    TopicTemplateListData,
    TopicTemplateListResponse,
    TopicTemplateSummary,
)
from app.common.response import build_success_response
from app.services.topic_template_service import get_topic_template, list_topic_templates

router = APIRouter(tags=["TopicTemplates"])


@router.get("/topic-templates", response_model=TopicTemplateListResponse)
def list_active_topic_templates() -> dict:
    items = [TopicTemplateSummary.model_validate(item) for item in list_topic_templates()]
    return build_success_response(
        data=TopicTemplateListData(items=items).model_dump(),
    )


@router.get("/topic-templates/{template_id}", response_model=TopicTemplateDetailResponse)
def get_topic_template_detail(template_id: str) -> dict:
    template = get_topic_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="topic template not found")

    return build_success_response(
        data=TopicTemplateDetail.model_validate(template).model_dump(),
    )
