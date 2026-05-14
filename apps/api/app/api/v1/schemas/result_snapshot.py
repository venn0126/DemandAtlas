from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from app.api.v1.schemas.topic_template import ApiMeta


class ResolvedTimeWindow(BaseModel):
    start_at: str
    end_at: str

    model_config = ConfigDict(extra="forbid")


class SummaryStats(BaseModel):
    cluster_count: int | None = None
    post_count: int | None = None
    comment_count: int | None = None

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
    meta: ApiMeta = ApiMeta()
    error: None = None

    model_config = ConfigDict(extra="forbid")
