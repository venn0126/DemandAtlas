from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class ApiMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ApiError(BaseModel):
    code: str
    message: str
    details: dict | None = None

    model_config = ConfigDict(extra="forbid")


class TopicTemplateSummary(BaseModel):
    template_id: str
    template_version_id: str
    name: str
    description: str | None = None
    default_language: str
    default_view_type: Literal["active", "new"]

    model_config = ConfigDict(extra="forbid")


class TopicTemplateDetail(TopicTemplateSummary):
    candidate_subreddit_count: int | None = None

    model_config = ConfigDict(extra="forbid")


class TopicTemplateListData(BaseModel):
    items: list[TopicTemplateSummary]

    model_config = ConfigDict(extra="forbid")


class TopicTemplateListResponse(BaseModel):
    request_id: str
    data: TopicTemplateListData
    meta: ApiMeta = ApiMeta()
    error: None = None

    model_config = ConfigDict(extra="forbid")


class TopicTemplateDetailResponse(BaseModel):
    request_id: str
    data: TopicTemplateDetail
    meta: ApiMeta = ApiMeta()
    error: None = None

    model_config = ConfigDict(extra="forbid")


class ErrorResponse(BaseModel):
    request_id: str
    data: None = None
    meta: ApiMeta = ApiMeta()
    error: ApiError

    model_config = ConfigDict(extra="forbid")
