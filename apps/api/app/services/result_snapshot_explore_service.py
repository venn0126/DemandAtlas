from __future__ import annotations

from uuid import UUID
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.result_snapshot_repository import get_result_snapshot_by_id

DEMO_BOARD_MAP: dict[tuple[str, str], dict[str, Any]] = {}
DEMO_CLUSTER_MAP: dict[tuple[str, str], dict[str, Any]] = {}

_BOARD_PROFILES = {
    "hot": {
        "titles": ["Users still prefer wired workflows for reliability", "Teams still want better action-item extraction"],
        "score_boost": 12.0,
    },
    "growth": {
        "titles": ["Privacy-first offline workflows are gaining attention", "Demand for lightweight automation is accelerating"],
        "score_boost": 18.0,
    },
    "opportunity": {
        "titles": ["Users want simpler low-friction routines", "Teams want fewer manual follow-up steps"],
        "score_boost": 9.0,
    },
}


def _build_evidence(cluster_id: str, subreddit: str, excerpt: str, created_at: str) -> dict[str, Any]:
    return {
        "evidence_id": f"ev_{cluster_id}_{subreddit.lower()}",
        "excerpt": excerpt,
        "subreddit": subreddit,
        "created_at": created_at,
        "availability_status": "public",
        "source_url": f"https://reddit.com/r/{subreddit}/comments/{cluster_id.lower()}",
    }


def _build_board_items(snapshot: Any, board_type: str) -> list[dict[str, Any]]:
    summary_stats = snapshot.summary_stats or {}
    template_snapshot = snapshot.template_snapshot or {}
    pipeline_metadata = template_snapshot.get("pipeline_metadata") or {}
    source_scope = pipeline_metadata.get("source_scope") or {}
    keywords = source_scope.get("keywords") or []
    subreddits = source_scope.get("subreddits") or []
    coverage = pipeline_metadata.get("coverage") or {}
    result_profile = pipeline_metadata.get("result_profile") or {}

    cluster_count = max(1, min(2, result_profile.get("cluster_count") or summary_stats.get("cluster_count") or 1))
    post_count = summary_stats.get("post_count") or 12
    comment_count = summary_stats.get("comment_count") or 48
    subreddit_pool = subreddits or ["productivity", "artificial"]
    requested_count = coverage.get("requested_source_count") or len(subreddit_pool) or len(keywords) or 1
    base_source_count = max(requested_count, 1)
    titles = _BOARD_PROFILES[board_type]["titles"]
    score_boost = _BOARD_PROFILES[board_type]["score_boost"]

    items: list[dict[str, Any]] = []
    for idx in range(cluster_count):
        cluster_id = f"clu_{str(snapshot.id).replace('-', '')[:12]}_{board_type}_{idx + 1}"
        primary_subreddit = subreddit_pool[idx % len(subreddit_pool)]
        title = titles[idx % len(titles)]
        unique_user_count = max(8, post_count // (idx + 2))
        board_score = round(60.0 + score_boost - idx * 3.5, 1)
        item = {
            "rank": idx + 1,
            "cluster_id": cluster_id,
            "title": title,
            "summary": f"{title} The current placeholder snapshot indicates repeated demand across {base_source_count} source scopes.",
            "board_score": board_score,
            "discussion_score": round(board_score - 5.0, 1),
            "attention_score": round(board_score - 8.0, 1),
            "growth_score": round(board_score - (14.0 if board_type == 'hot' else 3.0), 1),
            "opportunity_score": round(board_score - (5.0 if board_type == 'opportunity' else 8.0), 1),
            "confidence_score": round(88.0 - idx * 7.0, 1),
            "post_count": max(1, post_count // (idx + 1)),
            "comment_count": max(1, comment_count // (idx + 1)),
            "unique_user_count": unique_user_count,
            "is_weak_signal": False,
            "is_low_confidence": board_type == "opportunity" and idx == cluster_count - 1,
            "is_emerging_signal": board_type == "growth" and idx == 0,
            "top_subreddits": subreddit_pool[: min(3, len(subreddit_pool))],
            "highlight_evidence": [
                _build_evidence(
                    cluster_id,
                    primary_subreddit,
                    f"Representative evidence for {title.lower()}",
                    snapshot.generated_at.isoformat(),
                )
            ],
        }
        items.append(item)

    return items


def _build_cluster_detail(snapshot: Any, board_type: str, cluster_id: str) -> dict[str, Any] | None:
    items = _build_board_items(snapshot, board_type)
    item = next((entry for entry in items if entry["cluster_id"] == cluster_id), None)
    if item is None:
        return None

    coverage_note = snapshot.coverage_note
    source_scope = (snapshot.template_snapshot or {}).get("pipeline_metadata", {}).get("source_scope") or {}
    top_subreddits = item["top_subreddits"]

    return {
        "cluster_id": item["cluster_id"],
        "title": item["title"],
        "summary": item["summary"],
        "time_window": {
            "start_at": snapshot.query_task.window_start.isoformat() if snapshot.query_task else snapshot.generated_at.isoformat(),
            "end_at": snapshot.query_task.window_end.isoformat() if snapshot.query_task else snapshot.generated_at.isoformat(),
        },
        "flags": {
            "is_weak_signal": item["is_weak_signal"],
            "is_low_confidence": item["is_low_confidence"],
            "is_emerging_signal": item["is_emerging_signal"],
        },
        "scores": {
            "discussion_score": item["discussion_score"],
            "attention_score": item["attention_score"],
            "growth_score": item["growth_score"],
            "opportunity_score": item["opportunity_score"],
            "confidence_score": item["confidence_score"],
        },
        "metrics": {
            "post_count": item["post_count"],
            "comment_count": item["comment_count"],
            "unique_user_count": item["unique_user_count"],
            "community_spread_count": max(1, len(top_subreddits)),
        },
        "scenes": ["analysis", "prioritization", "follow-up"],
        "pain_points": [
            "manual synthesis overhead",
            "low confidence on weakly structured evidence",
            "cross-source consistency checks",
        ],
        "alternatives": ["manual review", "lighter-weight tooling", "spreadsheet tracking"],
        "supporting_evidence": item["highlight_evidence"],
        "opposing_evidence": [
            _build_evidence(
                item["cluster_id"],
                top_subreddits[0],
                f"Counterpoint evidence for {item['title'].lower()}",
                snapshot.generated_at.isoformat(),
            )
        ],
        "top_subreddits": top_subreddits,
        "coverage_note": coverage_note,
    }


def get_result_snapshot_board_from_db(
    db: Session,
    result_snapshot_id: str,
    board_type: str,
) -> dict[str, Any] | None:
    if board_type not in _BOARD_PROFILES:
        return None

    try:
        snapshot_uuid = UUID(result_snapshot_id)
    except ValueError:
        return None

    snapshot = get_result_snapshot_by_id(db, snapshot_uuid)
    if snapshot is None:
        return None

    items = _build_board_items(snapshot, board_type)
    warning_items = (snapshot.template_snapshot or {}).get("warnings") or []

    return {
        "data": {
            "board_type": board_type,
            "items": items,
        },
        "meta": {
            "response_source": "database",
            "next_page_token": None,
            "warning_count": len(warning_items),
        },
        "error": None,
    }


def get_demo_result_snapshot_board(result_snapshot_id: str, board_type: str) -> dict[str, Any] | None:
    payload = DEMO_BOARD_MAP.get((result_snapshot_id, board_type))
    if payload is None:
        return None
    return {
        **payload,
        "meta": {
            **payload["meta"],
            "response_source": "demo_static",
        },
    }


def get_cluster_detail_from_db(
    db: Session,
    result_snapshot_id: str,
    cluster_id: str,
) -> dict[str, Any] | None:
    try:
        snapshot_uuid = UUID(result_snapshot_id)
    except ValueError:
        return None

    snapshot = get_result_snapshot_by_id(db, snapshot_uuid)
    if snapshot is None:
        return None

    available_boards = ["hot", "growth", "opportunity"]
    detail = None
    for board_type in available_boards:
        detail = _build_cluster_detail(snapshot, board_type, cluster_id)
        if detail is not None:
            break
    if detail is None:
        return None

    warning_items = (snapshot.template_snapshot or {}).get("warnings") or []
    return {
        "data": detail,
        "meta": {
            "response_source": "database",
            "evidence_next_page_token": None,
            "warning_count": len(warning_items),
        },
        "error": None,
    }


def get_demo_cluster_detail(result_snapshot_id: str, cluster_id: str) -> dict[str, Any] | None:
    payload = DEMO_CLUSTER_MAP.get((result_snapshot_id, cluster_id))
    if payload is None:
        return None
    return {
        **payload,
        "meta": {
            **payload["meta"],
            "response_source": "demo_static",
        },
    }
