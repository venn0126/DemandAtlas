from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from worker.pipeline.stages import FINALIZING_STAGE, PIPELINE_STAGES


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _normalized_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _build_summary_stats(query_input: dict[str, Any]) -> dict[str, int]:
    query_type = query_input.get("query_type", "directed")
    keyword_count = len(_normalized_string_list(query_input.get("keywords")))
    subreddit_count = len(_normalized_string_list(query_input.get("subreddits")))

    if query_type == "one_click":
        return {
            "cluster_count": 11,
            "post_count": 141,
            "comment_count": 1094,
        }

    source_scope = subreddit_count or max(keyword_count, 1)
    cluster_count = max(1, min(18, keyword_count * 3 + source_scope))
    post_count = cluster_count * max(keyword_count + 2, 4)
    comment_count = post_count * max(keyword_count + 3, 5)

    return {
        "cluster_count": cluster_count,
        "post_count": post_count,
        "comment_count": comment_count,
    }


def _build_coverage_note(query_input: dict[str, Any], outcome_status: str) -> str | None:
    query_type = query_input.get("query_type", "directed")
    subreddit_count = len(_normalized_string_list(query_input.get("subreddits")))

    if outcome_status == "failed":
        return None
    if outcome_status == "partial_success":
        if subreddit_count > 0:
            return "partial coverage: 1 requested subreddit unavailable during fetch"
        return "partial coverage: 1 candidate source unavailable during fetch"
    if query_type == "one_click":
        return "cache-backed one-click coverage completed"
    if subreddit_count > 0:
        return f"full coverage on {subreddit_count} requested subreddits"
    return "full coverage on candidate sources"


def _build_sync_freshness_note() -> str:
    return f"latest source sync at {utc_now_iso()}"


def _build_available_boards(summary_stats: dict[str, int]) -> list[str]:
    cluster_count = summary_stats.get("cluster_count", 0)
    if cluster_count <= 0:
        return ["hot"]
    if cluster_count < 3:
        return ["hot", "growth"]
    return ["hot", "growth", "opportunity"]


def _build_stage_message(
    stage: str,
    *,
    query_input: dict[str, Any],
    summary_stats: dict[str, int],
    outcome_status: str,
) -> str:
    keyword_count = len(_normalized_string_list(query_input.get("keywords")))
    subreddit_count = len(_normalized_string_list(query_input.get("subreddits")))
    source_scope = subreddit_count or max(keyword_count, 1)

    if stage == "validate":
        return (
            f"validated {query_input.get('query_type', 'directed')} query "
            f"with {keyword_count} keywords"
        )
    if stage == "plan":
        return f"planned placeholder execution across {source_scope} source scopes"
    if stage == "fetch":
        if outcome_status == "partial_success":
            return f"fetched placeholder source documents from {source_scope - 1}/{source_scope} scopes"
        return f"fetched placeholder source documents from {source_scope} scopes"
    if stage == "normalize":
        return "normalized placeholder source documents"
    if stage == "retrieve":
        return f"retrieved placeholder candidates for {summary_stats['cluster_count']} clusters"
    if stage == "cluster":
        return f"built {summary_stats['cluster_count']} placeholder clusters"
    if stage == "score":
        return f"scored {summary_stats['cluster_count']} placeholder clusters"
    if stage == "snapshot":
        return (
            "assembled placeholder snapshot with "
            f"{summary_stats['post_count']} posts and {summary_stats['comment_count']} comments"
        )
    return f"{stage} stage completed in placeholder mode"


def _determine_pipeline_outcome(query_input: dict[str, Any]) -> tuple[str, str | None]:
    query_type = query_input.get("query_type", "directed")
    keyword_count = len(_normalized_string_list(query_input.get("keywords")))
    subreddit_count = len(_normalized_string_list(query_input.get("subreddits")))

    if query_type == "directed" and keyword_count == 0:
        return "failed", "directed query requires at least one keyword"

    if query_type == "directed" and subreddit_count >= 3:
        return "partial_success", None

    return "success", None


def build_pipeline_plan(query_task_id: str) -> dict[str, Any]:
    return {
        "query_task_id": query_task_id,
        "pipeline_stages": list(PIPELINE_STAGES),
        "finalize_stage": FINALIZING_STAGE,
        "created_at": utc_now_iso(),
    }


def run_pipeline(query_task_id: str, query_input: dict[str, Any]) -> dict[str, Any]:
    timeline: list[dict[str, Any]] = []
    summary_stats = _build_summary_stats(query_input)
    outcome_status, failure_reason = _determine_pipeline_outcome(query_input)
    coverage_note = _build_coverage_note(query_input, outcome_status)
    sync_freshness_note = _build_sync_freshness_note()
    available_boards = _build_available_boards(summary_stats)

    for index, stage in enumerate(PIPELINE_STAGES, start=1):
        stage_status = "success"
        stage_message = _build_stage_message(
            stage,
            query_input=query_input,
            summary_stats=summary_stats,
            outcome_status=outcome_status,
        )
        stage_meta: dict[str, Any] = {
            "query_type": query_input.get("query_type", "directed"),
            "summary_stats": summary_stats if stage == "snapshot" else None,
        }

        if outcome_status == "failed" and stage == "validate":
            stage_status = "failed"
            stage_message = failure_reason or "validation failed"
            stage_meta["failure_reason"] = failure_reason
        elif outcome_status == "partial_success" and stage == "fetch":
            stage_status = "partial_success"
            stage_meta["coverage_note"] = coverage_note

        timeline.append(
            {
                "stage": stage,
                "status": stage_status,
                "started_at": utc_now_iso(),
                "finished_at": utc_now_iso(),
                "current_step": index,
                "total_steps": len(PIPELINE_STAGES),
                "message": stage_message,
                "meta": stage_meta,
            }
        )

        if stage_status == "failed":
            break

    timeline.append(
        {
            "stage": FINALIZING_STAGE,
            "status": outcome_status,
            "started_at": utc_now_iso(),
            "finished_at": utc_now_iso(),
            "current_step": timeline[-1]["current_step"] if timeline else 0,
            "total_steps": len(PIPELINE_STAGES),
            "message": (
                failure_reason
                if outcome_status == "failed"
                else "pipeline finalized in placeholder mode"
            ),
            "meta": {
                "coverage_note": coverage_note,
                "available_boards": available_boards,
                "failure_reason": failure_reason,
            },
        }
    )

    current_step = timeline[-1]["current_step"] if timeline else 0
    percent = int((current_step / len(PIPELINE_STAGES)) * 100) if current_step else 0

    return {
        "query_task_id": query_task_id,
        "status": outcome_status,
        "current_stage": FINALIZING_STAGE,
        "progress": {
            "current_step": current_step,
            "total_steps": len(PIPELINE_STAGES),
            "percent": 100 if outcome_status in {"success", "partial_success"} else percent,
        },
        "timeline": timeline,
        "result_snapshot_id": None,
        "coverage_note": coverage_note,
        "sync_freshness_note": sync_freshness_note,
        "summary_stats": summary_stats,
        "available_boards": available_boards,
        "warnings": (
            []
            if outcome_status == "success"
            else [
                {
                    "code": "PARTIAL_COVERAGE" if outcome_status == "partial_success" else "PIPELINE_FAILED",
                    "message": coverage_note or failure_reason or "pipeline completed with warnings",
                }
            ]
        ),
        "failure_reason": failure_reason,
    }
