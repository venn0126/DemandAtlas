from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.result_snapshot import SnapshotPipelineMetadata
from app.api.v1.schemas.topic_template import ApiError, ApiMeta


class TimeWindowPreset(BaseModel):
    preset: Literal["7d", "30d", "90d"]

    model_config = ConfigDict(extra="forbid")


class TimeWindowRange(BaseModel):
    start_at: str
    end_at: str

    model_config = ConfigDict(extra="forbid")


TimeWindow = Annotated[TimeWindowPreset | TimeWindowRange, Field(discriminator=None)]


class MinEngagementThreshold(BaseModel):
    min_post_score: int | None = None
    min_comment_count: int | None = None

    model_config = ConfigDict(extra="forbid")


class OneClickQueryTaskCreateRequest(BaseModel):
    query_type: Literal["one_click"]
    template_id: str
    template_version_id: str | None = None
    view_type: Literal["active", "new"] | None = None
    time_window: TimeWindowPreset | TimeWindowRange
    force_refresh: bool = False

    model_config = ConfigDict(extra="forbid")


class DirectedQueryTaskCreateRequest(BaseModel):
    query_type: Literal["directed"]
    keywords: list[str]
    subreddits: list[str] = Field(default_factory=list)
    language: str = "en"
    region_hints: list[str] = Field(default_factory=list)
    min_engagement_threshold: MinEngagementThreshold | None = None
    view_type: Literal["active", "new"] | None = None
    time_window: TimeWindowPreset | TimeWindowRange
    force_refresh: bool = False

    model_config = ConfigDict(extra="forbid")


class QueryTaskCreateCacheHitData(BaseModel):
    execution_mode: Literal["cache_hit"]
    query_task_id: str
    status: Literal["success", "partial_success"]
    result_snapshot_id: str
    cached: bool

    model_config = ConfigDict(extra="forbid")


class QueryTaskCreateAcceptedData(BaseModel):
    execution_mode: Literal["async"]
    query_task_id: str
    status: Literal["pending", "running"]
    poll_url: str
    anonymous_query_access_token: str

    model_config = ConfigDict(extra="forbid")


class QueryTaskCreateCacheHitResponse(BaseModel):
    request_id: str
    data: QueryTaskCreateCacheHitData
    meta: ApiMeta = ApiMeta()
    error: None = None

    model_config = ConfigDict(extra="forbid")


class QueryTaskCreateAcceptedResponse(BaseModel):
    request_id: str
    data: QueryTaskCreateAcceptedData
    meta: ApiMeta = ApiMeta()
    error: None = None

    model_config = ConfigDict(extra="forbid")


class ErrorResponse(BaseModel):
    request_id: str
    data: None = None
    meta: ApiMeta = ApiMeta()
    error: ApiError

    model_config = ConfigDict(extra="forbid")


class QueryProgress(BaseModel):
    current_step: int | None = None
    total_steps: int | None = None
    percent: int | None = None

    model_config = ConfigDict(extra="forbid")


class WarningItem(BaseModel):
    code: str
    message: str

    model_config = ConfigDict(extra="forbid")


class QueryTaskStatusMeta(BaseModel):
    response_source: Literal["database", "demo_static"] | None = None
    pipeline_metadata: SnapshotPipelineMetadata | None = None
    warning_count: int | None = None
    coverage_status: Literal["success", "partial_success", "failed"] | None = None
    requested_source_count: int | None = None
    completed_source_count: int | None = None
    source_scope_count: int | None = None
    result_cluster_count: int | None = None

    model_config = ConfigDict(extra="forbid")


class QueryTaskStatusData(BaseModel):
    query_task_id: str
    status: Literal["pending", "running", "partial_success", "success", "failed"]
    current_stage: str | None = None
    progress: QueryProgress | None = None
    result_snapshot_id: str | None = None
    coverage_note: str | None = None
    warnings: list[WarningItem] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class QueryTaskStatusResponse(BaseModel):
    request_id: str
    data: QueryTaskStatusData
    meta: QueryTaskStatusMeta = QueryTaskStatusMeta()
    error: ApiError | None = None

    model_config = ConfigDict(extra="forbid")
