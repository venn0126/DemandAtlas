from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class ResolvedTimeWindow(BaseModel):
    start_at: str
    end_at: str

    model_config = ConfigDict(extra="forbid")


class SummaryStats(BaseModel):
    cluster_count: int | None = None
    post_count: int | None = None
    comment_count: int | None = None

    model_config = ConfigDict(extra="forbid")


class PipelineSourceScope(BaseModel):
    keywords: list[str] = []
    subreddits: list[str] = []
    source_count: int | None = None

    model_config = ConfigDict(extra="forbid")


class PipelineCoverage(BaseModel):
    status: Literal["success", "partial_success", "failed"] | None = None
    requested_source_count: int | None = None
    completed_source_count: int | None = None

    model_config = ConfigDict(extra="forbid")


class PipelineResultProfile(BaseModel):
    cluster_count: int | None = None
    post_count: int | None = None
    comment_count: int | None = None

    model_config = ConfigDict(extra="forbid")


class SnapshotPipelineMetadata(BaseModel):
    query_type: Literal["one_click", "directed"] | None = None
    execution_mode: str | None = None
    source_scope: PipelineSourceScope | None = None
    coverage: PipelineCoverage | None = None
    result_profile: PipelineResultProfile | None = None

    model_config = ConfigDict(extra="forbid")


class ResultSnapshotSummaryMeta(BaseModel):
    response_source: Literal["database", "demo_static"] | None = None
    pipeline_metadata: SnapshotPipelineMetadata | None = None
    warning_count: int | None = None

    model_config = ConfigDict(extra="forbid")


class ResultSnapshotSummary(BaseModel):
    result_snapshot_id: str
    query_task_id: str
    query_type: Literal["one_click", "directed"] | None = None
    view_type: Literal["active", "new"]
    time_window: ResolvedTimeWindow | None = None
    generated_at: str
    coverage_note: str | None = None
    sync_freshness_note: str | None = None
    summary_stats: SummaryStats | None = None
    available_boards: list[Literal["hot", "growth", "opportunity"]] = []

    model_config = ConfigDict(extra="forbid")


class ResultSnapshotSummaryResponse(BaseModel):
    request_id: str
    data: ResultSnapshotSummary
    meta: ResultSnapshotSummaryMeta = ResultSnapshotSummaryMeta()
    error: None = None

    model_config = ConfigDict(extra="forbid")
