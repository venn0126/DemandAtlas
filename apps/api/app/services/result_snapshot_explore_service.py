from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.result_snapshot_repository import (
    get_cluster_detail_bundle,
    get_result_snapshot_by_id,
    list_snapshot_board_entries,
)

DEMO_BOARD_MAP: dict[tuple[str, str], dict[str, Any]] = {}
DEMO_CLUSTER_MAP: dict[tuple[str, str], dict[str, Any]] = {}

_BOARD_TYPES = {"hot", "growth", "opportunity"}


def _to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _build_evidence_payload(evidence: Any) -> dict[str, Any]:
    return {
        "evidence_id": str(evidence.id),
        "excerpt": evidence.excerpt,
        "subreddit": evidence.subreddit_name,
        "created_at": evidence.source_created_at.isoformat(),
        "availability_status": evidence.availability_status,
        "source_url": evidence.source_url,
    }


def _top_subreddits_from_evidence(evidences: list[Any], *, limit: int) -> list[str]:
    return list(dict.fromkeys(evidence.subreddit_name for evidence in evidences))[:limit]


def get_result_snapshot_board_from_db(
    db: Session,
    result_snapshot_id: str,
    board_type: str,
) -> dict[str, Any] | None:
    if board_type not in _BOARD_TYPES:
        return None

    try:
        snapshot_uuid = UUID(result_snapshot_id)
    except ValueError:
        return None

    snapshot = get_result_snapshot_by_id(db, snapshot_uuid)
    if snapshot is None:
        return None

    rows = list_snapshot_board_entries(
        db,
        result_snapshot_id=snapshot_uuid,
        board_type=board_type,
    )
    warning_items = (snapshot.template_snapshot or {}).get("warnings") or []

    items = []
    for entry, cluster, metric in rows:
        evidence_pool = sorted(
            cluster.evidences,
            key=lambda item: (
                item.score_hint is not None,
                item.score_hint or 0,
                item.source_created_at,
            ),
            reverse=True,
        )
        highlight_evidence = [
            _build_evidence_payload(evidence)
            for evidence in evidence_pool
            if evidence.stance == "support"
        ][:2]
        top_subreddits = _top_subreddits_from_evidence(evidence_pool, limit=3)

        if metric is None:
            continue

        items.append(
            {
                "rank": entry.rank_no,
                "cluster_id": str(cluster.id),
                "title": cluster.canonical_title,
                "summary": cluster.summary,
                "board_score": _to_float(entry.board_score),
                "discussion_score": _to_float(metric.discussion_score),
                "attention_score": _to_float(metric.attention_score),
                "growth_score": _to_float(metric.growth_score),
                "opportunity_score": _to_float(metric.opportunity_score),
                "confidence_score": _to_float(cluster.confidence_score),
                "post_count": metric.post_count,
                "comment_count": metric.comment_count,
                "unique_user_count": metric.unique_user_count,
                "is_weak_signal": metric.is_weak_signal,
                "is_low_confidence": metric.is_low_confidence,
                "is_emerging_signal": metric.is_emerging_signal,
                "top_subreddits": top_subreddits,
                "highlight_evidence": highlight_evidence,
            }
        )

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


def get_demo_result_snapshot_board(
    result_snapshot_id: str,
    board_type: str,
) -> dict[str, Any] | None:
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
        cluster_uuid = UUID(cluster_id)
    except ValueError:
        return None

    snapshot = get_result_snapshot_by_id(db, snapshot_uuid)
    if snapshot is None:
        return None

    bundle = get_cluster_detail_bundle(
        db,
        result_snapshot_id=snapshot_uuid,
        cluster_id=cluster_uuid,
    )
    if bundle is None:
        return None

    cluster, metric, evidences, board_entries = bundle
    if metric is None:
        return None

    supporting = [
        _build_evidence_payload(evidence)
        for evidence in evidences
        if evidence.stance == "support"
    ]
    opposing = [
        _build_evidence_payload(evidence)
        for evidence in evidences
        if evidence.stance == "oppose"
    ]
    top_subreddits = _top_subreddits_from_evidence(evidences, limit=5)
    warning_items = (snapshot.template_snapshot or {}).get("warnings") or []

    return {
        "data": {
            "cluster_id": str(cluster.id),
            "title": cluster.canonical_title,
            "summary": cluster.summary,
            "time_window": {
                "start_at": metric.window_start.isoformat(),
                "end_at": metric.window_end.isoformat(),
            },
            "flags": {
                "is_weak_signal": metric.is_weak_signal,
                "is_low_confidence": metric.is_low_confidence,
                "is_emerging_signal": metric.is_emerging_signal,
            },
            "scores": {
                "discussion_score": _to_float(metric.discussion_score),
                "attention_score": _to_float(metric.attention_score),
                "growth_score": _to_float(metric.growth_score),
                "opportunity_score": _to_float(metric.opportunity_score),
                "confidence_score": _to_float(cluster.confidence_score),
            },
            "metrics": {
                "post_count": metric.post_count,
                "comment_count": metric.comment_count,
                "unique_user_count": metric.unique_user_count,
                "community_spread_count": metric.community_spread_count,
            },
            "scenes": cluster.scenes,
            "pain_points": cluster.pain_points,
            "alternatives": cluster.alternatives,
            "supporting_evidence": supporting,
            "opposing_evidence": opposing,
            "top_subreddits": top_subreddits,
            "coverage_note": snapshot.coverage_note,
        },
        "meta": {
            "response_source": "database",
            "evidence_next_page_token": None,
            "warning_count": len(warning_items),
            "boards": [entry.board_type for entry in board_entries],
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
