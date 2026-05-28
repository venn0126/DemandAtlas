from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from worker.fetch.reddit_connector import RedditConnector
from worker.pipeline.analyzer import build_clusters
from worker.pipeline.stages import FINALIZING_STAGE, PIPELINE_STAGES
from worker.pipeline.template_loader import load_topic_template_runtime
from worker.pipeline.types import (
    FetchWarning,
    QueryExecutionPlan,
    SourceComment,
    SourcePost,
)


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _normalized_string_list(value: Any) -> list[str]:
    if isinstance(value, dict):
        value = value.get("items") or value.get("terms") or []
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _resolve_plan(
    query_input: dict[str, Any],
    query_task_context: dict[str, Any],
) -> QueryExecutionPlan:
    query_type = query_task_context.get("query_type") or query_input.get("query_type", "directed")
    language = query_task_context.get("language") or query_input.get("language", "en")
    view_type = query_task_context.get("view_type") or query_input.get("view_type", "active")
    region_hints = _normalized_string_list(
        query_task_context.get("region_hints", {}).get("items")
        if isinstance(query_task_context.get("region_hints"), dict)
        else query_input.get("region_hints")
    )

    keywords = _normalized_string_list(query_input.get("keywords"))
    subreddits = _normalized_string_list(query_input.get("subreddits"))
    template_id = query_input.get("template_id")
    template_version_id = query_input.get("template_version_id")

    if query_type == "one_click":
        template = load_topic_template_runtime(template_id or "tpl_ai_tools", template_version_id)
        keywords = template.keywords + template.synonyms
        subreddits = template.candidate_subreddits
        language = template.default_language
        view_type = query_input.get("view_type") or template.default_view_type
        template_version_id = template.template_version_id
    source_scope = subreddits or keywords[:3]

    return QueryExecutionPlan(
        query_type=query_type,
        template_id=template_id,
        template_version_id=template_version_id,
        view_type=view_type,
        language=language,
        keywords=keywords,
        subreddits=subreddits,
        region_hints=region_hints,
        min_engagement_threshold=query_task_context.get("min_engagement_threshold") or {},
        window_start=query_task_context["window_start"],
        window_end=query_task_context["window_end"],
        compare_window_start=query_task_context.get("compare_window_start"),
        compare_window_end=query_task_context.get("compare_window_end"),
        source_scope=source_scope,
    )


def _build_summary_stats(
    posts: list[SourcePost],
    comments: list[SourceComment],
    cluster_count: int,
) -> dict[str, int]:
    return {
        "cluster_count": cluster_count,
        "post_count": len(posts),
        "comment_count": len(comments),
    }


def _build_pipeline_metadata(
    plan: QueryExecutionPlan,
    *,
    outcome_status: str,
    summary_stats: dict[str, int],
    completed_source_count: int,
    execution_mode: str,
) -> dict[str, Any]:
    return {
        "query_type": plan.query_type,
        "execution_mode": execution_mode,
        "source_scope": {
            "keywords": plan.keywords,
            "subreddits": plan.subreddits,
            "source_count": len(plan.source_scope),
        },
        "coverage": {
            "status": outcome_status,
            "requested_source_count": len(plan.source_scope),
            "completed_source_count": completed_source_count,
        },
        "result_profile": {
            "cluster_count": summary_stats["cluster_count"],
            "post_count": summary_stats["post_count"],
            "comment_count": summary_stats["comment_count"],
        },
    }


def _build_coverage_note(
    plan: QueryExecutionPlan,
    warnings: list[FetchWarning],
    cluster_count: int,
) -> str | None:
    if cluster_count == 0:
        return "no valid clusters were formed from available sources"

    if warnings:
        missing_count = len(
            [warning for warning in warnings if warning.code == "SOURCE_FETCH_PARTIAL"]
        )
        if missing_count > 0:
            if plan.subreddits:
                return (
                    f"partial coverage: {missing_count} requested subreddits "
                    "unavailable during fetch"
                )
            return f"partial coverage: {missing_count} candidate sources unavailable during fetch"
        return (
            "partial coverage: source fetch degraded and results were generated "
            "from fallback data"
        )

    if plan.subreddits:
        return f"full coverage on {len(plan.subreddits)} requested subreddits"
    return "full coverage on candidate sources"


def _build_available_boards(cluster_count: int) -> list[str]:
    if cluster_count <= 0:
        return ["hot"]
    if cluster_count < 2:
        return ["hot", "growth"]
    return ["hot", "growth", "opportunity"]


def _warning_items(
    fetch_warnings: list[FetchWarning],
    *,
    cluster_count: int | None = None,
) -> list[dict[str, str]]:
    items = [
        {
            "code": warning.code,
            "message": warning.message,
        }
        for warning in fetch_warnings
    ]
    if cluster_count is not None and cluster_count <= 0:
        items.append(
            {
                "code": "NO_RESULT_CLUSTER",
                "message": "no valid clusters were formed from available sources",
            }
        )
    return items


def _build_outcome_status(fetch_warnings: list[FetchWarning], cluster_count: int) -> str:
    if fetch_warnings or cluster_count <= 0:
        return "partial_success"
    return "success"


def _source_url_from_permalink(permalink: str) -> str:
    if permalink.startswith("/"):
        return f"https://reddit.com{permalink}"
    return permalink


def _normalize_posts(raw_posts: list[dict[str, Any]]) -> list[SourcePost]:
    normalized: list[SourcePost] = []
    for post in raw_posts:
        created_at = datetime.fromtimestamp(post.get("created_utc") or 0, UTC)
        permalink = post.get("permalink") or ""
        normalized.append(
            SourcePost(
                source_post_id=f"sp_{post['id']}",
                reddit_post_id=post["id"],
                subreddit=post.get("subreddit") or "unknown",
                title=post.get("title") or "",
                body=post.get("selftext") or "",
                author_ref=post.get("author") or "[deleted]",
                score=int(post.get("score") or 0),
                comment_count=int(post.get("num_comments") or 0),
                created_at=created_at,
                fetched_at=datetime.now(UTC),
                content_availability_status="public",
                is_crosspost=not bool(post.get("is_self", True)),
                is_pinned=bool(post.get("stickied") or False),
                is_nsfw=bool(post.get("over_18") or False),
                raw_payload_ref=f"raw/reddit/post/{post['id']}.json",
                source_url=_source_url_from_permalink(permalink),
                matched_keywords=post.get("matched_keywords") or [],
            )
        )
    return normalized


def _normalize_comments(raw_comments: list[dict[str, Any]]) -> list[SourceComment]:
    normalized: list[SourceComment] = []
    for comment in raw_comments:
        created_at = datetime.fromtimestamp(comment.get("created_utc") or 0, UTC)
        permalink = comment.get("permalink") or ""
        normalized.append(
            SourceComment(
                source_comment_id=f"sc_{comment['id']}",
                reddit_comment_id=comment["id"],
                reddit_post_id=(comment.get("link_id") or "").replace("t3_", ""),
                parent_comment_id=(comment.get("parent_id") or "").replace("t1_", "") or None,
                subreddit=comment.get("subreddit") or "unknown",
                body=comment.get("body") or "",
                author_ref=comment.get("author") or "[deleted]",
                score=int(comment.get("score") or 0),
                depth=int(comment.get("depth") or 0),
                created_at=created_at,
                fetched_at=datetime.now(UTC),
                content_availability_status="public",
                raw_payload_ref=f"raw/reddit/comment/{comment['id']}.json",
                source_url=_source_url_from_permalink(permalink),
                matched_keywords=comment.get("matched_keywords") or [],
            )
        )
    return normalized


def _filter_retrieved_posts(
    plan: QueryExecutionPlan,
    posts: list[SourcePost],
    comments: list[SourceComment],
) -> tuple[list[SourcePost], list[SourceComment]]:
    include_terms = [term.lower() for term in plan.keywords if term.strip()]
    exclude_terms = []
    if plan.query_type == "one_click":
        template = load_topic_template_runtime(
            plan.template_id or "tpl_ai_tools",
            plan.template_version_id,
        )
        exclude_terms = [term.lower() for term in template.exclude_terms]

    filtered_posts: list[SourcePost] = []
    allowed_post_ids: set[str] = set()
    for post in posts:
        text = f"{post.title}\n{post.body}".lower()
        if include_terms and not any(term in text for term in include_terms):
            continue
        if exclude_terms and any(term in text for term in exclude_terms):
            continue
        filtered_posts.append(post)
        allowed_post_ids.add(post.reddit_post_id)

    filtered_comments = [
        comment
        for comment in comments
        if comment.reddit_post_id in allowed_post_ids
        or any(term in comment.body.lower() for term in include_terms)
    ]
    return filtered_posts, filtered_comments


def _determine_outcome(
    posts: list[SourcePost],
    completed_source_count: int,
    source_count: int,
) -> tuple[str, str | None]:
    if source_count <= 0:
        return "failed", "no source scope resolved for query task"
    if completed_source_count <= 0 or not posts:
        return "failed", "unable to fetch any valid source data"
    if completed_source_count < source_count:
        return "partial_success", None
    return "success", None


def build_pipeline_plan(query_task_id: str) -> dict[str, Any]:
    return {
        "query_task_id": query_task_id,
        "pipeline_stages": list(PIPELINE_STAGES),
        "finalize_stage": FINALIZING_STAGE,
        "created_at": utc_now_iso(),
    }


def run_pipeline(
    query_task_id: str,
    query_input: dict[str, Any],
    query_task_context: dict[str, Any],
) -> dict[str, Any]:
    timeline: list[dict[str, Any]] = []
    plan = _resolve_plan(query_input, query_task_context)
    connector = RedditConnector()

    def append_stage(
        stage: str,
        *,
        status: str,
        message: str,
        meta: dict[str, Any] | None = None,
    ) -> None:
        index = len(timeline) + 1
        timeline.append(
            {
                "stage": stage,
                "status": status,
                "started_at": utc_now_iso(),
                "finished_at": utc_now_iso(),
                "current_step": index,
                "total_steps": len(PIPELINE_STAGES),
                "message": message,
                "meta": meta or {},
            }
        )

    if plan.query_type == "directed" and not plan.keywords:
        append_stage(
            "validate",
            status="failed",
            message="directed query requires at least one keyword",
            meta={"failure_reason": "directed query requires at least one keyword"},
        )
        failure_reason = "directed query requires at least one keyword"
        timeline.append(
            {
                "stage": FINALIZING_STAGE,
                "status": "failed",
                "started_at": utc_now_iso(),
                "finished_at": utc_now_iso(),
                "current_step": 1,
                "total_steps": len(PIPELINE_STAGES),
                "message": failure_reason,
                "meta": {"failure_reason": failure_reason},
            }
        )
        return {
            "query_task_id": query_task_id,
            "status": "failed",
            "current_stage": FINALIZING_STAGE,
            "progress": {
                "current_step": 1,
                "total_steps": len(PIPELINE_STAGES),
                "percent": 12,
            },
            "timeline": timeline,
            "result_snapshot_id": None,
            "coverage_note": None,
            "sync_freshness_note": None,
            "summary_stats": {"cluster_count": 0, "post_count": 0, "comment_count": 0},
            "available_boards": ["hot"],
            "warnings": [],
            "pipeline_metadata": {},
            "failure_reason": failure_reason,
            "query_plan": plan,
            "clusters": [],
        }

    append_stage(
        "validate",
        status="success",
        message=f"validated {plan.query_type} query with {len(plan.keywords)} keywords",
        meta={"query_type": plan.query_type},
    )
    append_stage(
        "plan",
        status="success",
        message=f"planned execution across {len(plan.source_scope)} source scopes",
        meta={
            "keywords": plan.keywords,
            "subreddits": plan.subreddits,
            "window_start": plan.window_start.isoformat(),
            "window_end": plan.window_end.isoformat(),
        },
    )

    fetch_payload = connector.fetch(plan)
    raw_posts = fetch_payload["posts"]
    raw_comments = fetch_payload["comments"]
    fetch_warnings: list[FetchWarning] = fetch_payload["warnings"]
    partial_warning_count = len(
        [warning for warning in fetch_warnings if warning.code == "SOURCE_FETCH_PARTIAL"]
    )
    completed_source_count = max(len(plan.source_scope) - partial_warning_count, 0)
    fetch_status, failure_reason = _determine_outcome(
        raw_posts,
        completed_source_count,
        len(plan.source_scope),
    )
    append_stage(
        "fetch",
        status=fetch_status if fetch_status != "success" else "success",
        message=(
            f"fetched {len(raw_posts)} posts and {len(raw_comments)} comments from "
            f"{completed_source_count}/{len(plan.source_scope)} scopes"
        ),
        meta={
            "completed_source_count": completed_source_count,
            "requested_source_count": len(plan.source_scope),
            "warning_count": len(fetch_warnings),
            "execution_mode": fetch_payload["execution_mode"],
        },
    )
    if fetch_status == "failed":
        timeline.append(
            {
                "stage": FINALIZING_STAGE,
                "status": "failed",
                "started_at": utc_now_iso(),
                "finished_at": utc_now_iso(),
                "current_step": 3,
                "total_steps": len(PIPELINE_STAGES),
                "message": failure_reason or "fetch failed",
                "meta": {"failure_reason": failure_reason},
            }
        )
        return {
            "query_task_id": query_task_id,
            "status": "failed",
            "current_stage": FINALIZING_STAGE,
            "progress": {"current_step": 3, "total_steps": len(PIPELINE_STAGES), "percent": 37},
            "timeline": timeline,
            "result_snapshot_id": None,
            "coverage_note": None,
            "sync_freshness_note": fetch_payload["sync_freshness_note"],
            "summary_stats": {"cluster_count": 0, "post_count": 0, "comment_count": 0},
            "available_boards": ["hot"],
            "warnings": _warning_items(fetch_warnings),
            "pipeline_metadata": {},
            "failure_reason": failure_reason,
            "query_plan": plan,
            "clusters": [],
        }

    normalized_posts = _normalize_posts(raw_posts)
    normalized_comments = _normalize_comments(raw_comments)
    append_stage(
        "normalize",
        status="success",
        message=f"normalized {len(normalized_posts)} posts and {len(normalized_comments)} comments",
        meta={"post_count": len(normalized_posts), "comment_count": len(normalized_comments)},
    )

    retrieved_posts, retrieved_comments = _filter_retrieved_posts(
        plan,
        normalized_posts,
        normalized_comments,
    )
    append_stage(
        "retrieve",
        status="success",
        message=(
            f"retrieved {len(retrieved_posts)} posts and "
            f"{len(retrieved_comments)} comments after filtering"
        ),
        meta={
            "retrieved_post_count": len(retrieved_posts),
            "retrieved_comment_count": len(retrieved_comments),
        },
    )

    clusters = build_clusters(plan=plan, posts=retrieved_posts, comments=retrieved_comments)
    append_stage(
        "cluster",
        status="success",
        message=f"built {len(clusters)} demand clusters",
        meta={"cluster_count": len(clusters)},
    )

    append_stage(
        "score",
        status="success",
        message=f"scored {len(clusters)} demand clusters",
        meta={"cluster_count": len(clusters)},
    )

    summary_stats = _build_summary_stats(retrieved_posts, retrieved_comments, len(clusters))
    available_boards = _build_available_boards(len(clusters))
    outcome_status = _build_outcome_status(fetch_warnings, len(clusters))
    coverage_note = _build_coverage_note(plan, fetch_warnings, len(clusters))
    pipeline_metadata = _build_pipeline_metadata(
        plan,
        outcome_status=outcome_status,
        summary_stats=summary_stats,
        completed_source_count=completed_source_count,
        execution_mode=fetch_payload["execution_mode"],
    )
    warning_items = _warning_items(fetch_warnings, cluster_count=len(clusters))
    append_stage(
        "snapshot",
        status="success",
        message=f"assembled snapshot for {len(clusters)} clusters",
        meta={
            "summary_stats": summary_stats,
            "pipeline_metadata": pipeline_metadata,
        },
    )
    timeline.append(
        {
            "stage": FINALIZING_STAGE,
            "status": outcome_status,
            "started_at": utc_now_iso(),
            "finished_at": utc_now_iso(),
            "current_step": len(PIPELINE_STAGES),
            "total_steps": len(PIPELINE_STAGES),
            "message": "pipeline finalized with real result tables",
            "meta": {
                "coverage_note": coverage_note,
                "available_boards": available_boards,
                "pipeline_metadata": pipeline_metadata,
                "warnings": warning_items,
            },
        }
    )

    return {
        "query_task_id": query_task_id,
        "status": outcome_status,
        "current_stage": FINALIZING_STAGE,
        "progress": {
            "current_step": len(PIPELINE_STAGES),
            "total_steps": len(PIPELINE_STAGES),
            "percent": 100,
        },
        "timeline": timeline,
        "result_snapshot_id": None,
        "coverage_note": coverage_note,
        "sync_freshness_note": fetch_payload["sync_freshness_note"],
        "summary_stats": summary_stats,
        "available_boards": available_boards,
        "warnings": warning_items,
        "pipeline_metadata": pipeline_metadata,
        "failure_reason": None,
        "query_plan": plan,
        "clusters": clusters,
    }
