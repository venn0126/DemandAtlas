from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass(slots=True)
class FetchWarning:
    code: str
    message: str
    source: str | None = None


@dataclass(slots=True)
class SourcePost:
    source_post_id: str
    reddit_post_id: str
    subreddit: str
    title: str
    body: str
    author_ref: str
    score: int
    comment_count: int
    created_at: datetime
    fetched_at: datetime
    content_availability_status: str
    is_crosspost: bool
    is_pinned: bool
    is_nsfw: bool
    raw_payload_ref: str
    source_url: str
    matched_keywords: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SourceComment:
    source_comment_id: str
    reddit_comment_id: str
    reddit_post_id: str
    parent_comment_id: str | None
    subreddit: str
    body: str
    author_ref: str
    score: int
    depth: int
    created_at: datetime
    fetched_at: datetime
    content_availability_status: str
    raw_payload_ref: str
    source_url: str
    matched_keywords: list[str] = field(default_factory=list)


@dataclass(slots=True)
class QueryExecutionPlan:
    query_type: str
    template_id: str | None
    template_version_id: str | None
    view_type: str
    language: str
    keywords: list[str]
    subreddits: list[str]
    region_hints: list[str]
    min_engagement_threshold: dict[str, Any]
    window_start: datetime
    window_end: datetime
    compare_window_start: datetime | None
    compare_window_end: datetime | None
    source_scope: list[str]


@dataclass(slots=True)
class ClusterEvidenceRecord:
    evidence_id: str
    source_type: str
    source_ref_id: str
    excerpt: str
    subreddit_name: str
    source_created_at: datetime
    stance: str
    availability_status: str
    source_url: str | None
    score_hint: Decimal | None


@dataclass(slots=True)
class ClusterRecord:
    cluster_key: str
    canonical_title: str
    summary: str
    scenes: list[str]
    pain_points: list[str]
    alternatives: list[str]
    sentiment_profile: dict[str, Any]
    confidence_score: Decimal
    first_seen_at: datetime
    last_seen_at: datetime
    aliases: list[str]
    post_count: int
    comment_count: int
    unique_user_count: int
    avg_comment_depth: Decimal
    avg_post_score: Decimal
    avg_comment_score: Decimal
    high_engagement_post_ratio: Decimal
    community_spread_count: int
    discussion_score: Decimal
    attention_score: Decimal
    growth_score: Decimal | None
    opportunity_score: Decimal | None
    is_weak_signal: bool
    is_low_confidence: bool
    is_emerging_signal: bool
    evidences: list[ClusterEvidenceRecord]
    board_scores: dict[str, Decimal]
    tie_break_meta: dict[str, Any]


@dataclass(slots=True)
class PipelineRuntimeResult:
    execution_mode: str
    available_boards: list[str]
    clusters: list[ClusterRecord]
    coverage_note: str | None
    warnings: list[dict[str, str]]
    pipeline_metadata: dict[str, Any]
    summary_stats: dict[str, int]
    sync_freshness_note: str | None
    source_posts: list[SourcePost]
    source_comments: list[SourceComment]
