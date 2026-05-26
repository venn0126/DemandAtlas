from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class EvidenceSnippet(BaseModel):
    evidence_id: str
    excerpt: str
    subreddit: str
    created_at: str
    availability_status: str
    source_url: str | None = None

    model_config = ConfigDict(extra="forbid")


class BoardEntry(BaseModel):
    rank: int
    cluster_id: str
    title: str
    summary: str | None = None
    board_score: float
    discussion_score: float | None = None
    attention_score: float | None = None
    growth_score: float | None = None
    opportunity_score: float | None = None
    confidence_score: float
    post_count: int
    comment_count: int
    unique_user_count: int
    is_weak_signal: bool
    is_low_confidence: bool
    is_emerging_signal: bool
    top_subreddits: list[str]
    highlight_evidence: list[EvidenceSnippet]

    model_config = ConfigDict(extra="forbid")


class BoardListData(BaseModel):
    board_type: Literal["hot", "growth", "opportunity"]
    items: list[BoardEntry]

    model_config = ConfigDict(extra="forbid")


class BoardListMeta(BaseModel):
    next_page_token: str | None = None
    response_source: Literal["database", "demo_static"] | None = None
    warning_count: int | None = None

    model_config = ConfigDict(extra="forbid")


class BoardListResponse(BaseModel):
    request_id: str
    data: BoardListData
    meta: BoardListMeta = BoardListMeta()
    error: None = None

    model_config = ConfigDict(extra="forbid")


class ClusterFlags(BaseModel):
    is_weak_signal: bool
    is_low_confidence: bool
    is_emerging_signal: bool

    model_config = ConfigDict(extra="forbid")


class ClusterScores(BaseModel):
    discussion_score: float | None = None
    attention_score: float | None = None
    growth_score: float | None = None
    opportunity_score: float | None = None
    confidence_score: float

    model_config = ConfigDict(extra="forbid")


class ClusterMetrics(BaseModel):
    post_count: int
    comment_count: int
    unique_user_count: int
    community_spread_count: int

    model_config = ConfigDict(extra="forbid")


class ClusterTimeWindow(BaseModel):
    start_at: str
    end_at: str

    model_config = ConfigDict(extra="forbid")


class DemandClusterDetail(BaseModel):
    cluster_id: str
    title: str
    summary: str
    time_window: ClusterTimeWindow
    flags: ClusterFlags
    scores: ClusterScores
    metrics: ClusterMetrics
    scenes: list[str]
    pain_points: list[str]
    alternatives: list[str]
    supporting_evidence: list[EvidenceSnippet]
    opposing_evidence: list[EvidenceSnippet]
    top_subreddits: list[str]
    coverage_note: str | None = None

    model_config = ConfigDict(extra="forbid")


class ClusterDetailMeta(BaseModel):
    evidence_next_page_token: str | None = None
    response_source: Literal["database", "demo_static"] | None = None
    warning_count: int | None = None
    boards: list[Literal["hot", "growth", "opportunity"]] = []

    model_config = ConfigDict(extra="forbid")


class ClusterDetailResponse(BaseModel):
    request_id: str
    data: DemandClusterDetail
    meta: ClusterDetailMeta = ClusterDetailMeta()
    error: None = None

    model_config = ConfigDict(extra="forbid")
