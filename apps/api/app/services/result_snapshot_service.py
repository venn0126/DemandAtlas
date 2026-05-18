from __future__ import annotations

from uuid import UUID
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.result_snapshot_repository import get_result_snapshot_by_id


RESULT_SNAPSHOT_SUMMARY_MAP: dict[str, dict[str, Any]] = {
    "rs_01JVA1T4WM4B3PG5N8W1HEP7QA": {
        "data": {
            "result_snapshot_id": "rs_01JVA1T4WM4B3PG5N8W1HEP7QA",
            "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
            "query_type": "directed",
            "view_type": "active",
            "time_window": {
                "start_at": "2026-04-01T00:00:00Z",
                "end_at": "2026-05-01T00:00:00Z",
            },
            "generated_at": "2026-05-12T09:12:00Z",
            "coverage_note": "full coverage on candidate sources",
            "sync_freshness_note": "latest source sync at 2026-05-12T08:47:00Z",
            "summary_stats": {
                "cluster_count": 18,
                "post_count": 236,
                "comment_count": 1943,
            },
            "available_boards": ["hot", "growth", "opportunity"],
        },
        "meta": {},
        "error": None,
    },
    "rs_01JVA2120R3D39SY1CMN18R8QW": {
        "data": {
            "result_snapshot_id": "rs_01JVA2120R3D39SY1CMN18R8QW",
            "query_task_id": "qt_01JVA20F4A1B31ANJVVKQJ0ZJ4",
            "query_type": "directed",
            "view_type": "active",
            "time_window": {
                "start_at": "2026-04-01T00:00:00Z",
                "end_at": "2026-05-01T00:00:00Z",
            },
            "generated_at": "2026-05-12T09:28:00Z",
            "coverage_note": "no valid clusters were formed from available sources",
            "sync_freshness_note": "latest source sync at 2026-05-12T09:20:00Z",
            "summary_stats": {
                "cluster_count": 0,
                "post_count": 8,
                "comment_count": 17,
            },
            "available_boards": ["hot"],
        },
        "meta": {},
        "error": None,
    },
    "rs_01JVA1PAB2Y9PGKQ7NH1AK6R9M": {
        "data": {
            "result_snapshot_id": "rs_01JVA1PAB2Y9PGKQ7NH1AK6R9M",
            "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
            "query_type": "one_click",
            "view_type": "active",
            "time_window": {
                "start_at": "2026-04-12T00:00:00Z",
                "end_at": "2026-05-12T00:00:00Z",
            },
            "generated_at": "2026-05-12T09:10:00Z",
            "coverage_note": "partial coverage: 2 candidate subreddits unavailable during fetch",
            "sync_freshness_note": "latest source sync at 2026-05-12T08:45:00Z",
            "summary_stats": {
                "cluster_count": 11,
                "post_count": 141,
                "comment_count": 1094,
            },
            "available_boards": ["hot", "growth"],
        },
        "meta": {},
        "error": None,
    },
}


def get_demo_result_snapshot_summary(result_snapshot_id: str) -> dict[str, Any] | None:
    payload = RESULT_SNAPSHOT_SUMMARY_MAP.get(result_snapshot_id)
    if payload is None:
        return None

    return {
        **payload,
        "meta": {
            **payload["meta"],
            "response_source": "demo_static",
        },
    }


def get_result_snapshot_summary_from_db(
    db: Session,
    result_snapshot_id: str,
) -> dict[str, Any] | None:
    try:
        snapshot_uuid = UUID(result_snapshot_id)
    except ValueError:
        return None

    snapshot = get_result_snapshot_by_id(db, snapshot_uuid)
    if snapshot is None:
        return None

    query_task = snapshot.query_task
    query_input = snapshot.query_input_snapshot or {}
    summary_stats = snapshot.summary_stats or {}
    cluster_count = summary_stats.get("cluster_count", 0)

    if cluster_count == 0:
        available_boards = ["hot"]
    elif (query_task.query_type if query_task else query_input.get("query_type")) == "one_click":
        available_boards = ["hot", "growth"]
    else:
        available_boards = ["hot", "growth", "opportunity"]

    if query_task is not None:
        query_type = query_task.query_type
        view_type = query_task.view_type
        time_window = {
            "start_at": query_task.window_start.isoformat(),
            "end_at": query_task.window_end.isoformat(),
        }
    else:
        query_type = query_input.get("query_type", "one_click")
        view_type = query_input.get("view_type", "active")
        time_window = {
            "start_at": query_input.get("time_window", {}).get("start_at")
            or snapshot.generated_at.isoformat(),
            "end_at": query_input.get("time_window", {}).get("end_at")
            or snapshot.generated_at.isoformat(),
        }

    return {
        "data": {
            "result_snapshot_id": str(snapshot.id),
            "query_task_id": str(snapshot.query_task_id),
            "query_type": query_type,
            "view_type": view_type,
            "time_window": time_window,
            "generated_at": snapshot.generated_at.isoformat(),
            "coverage_note": snapshot.coverage_note,
            "sync_freshness_note": snapshot.sync_freshness_note,
            "summary_stats": summary_stats,
            "available_boards": available_boards,
        },
        "meta": {
            "response_source": "database",
        },
        "error": None,
    }
