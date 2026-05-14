from __future__ import annotations

from typing import Any


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


def get_result_snapshot_summary(result_snapshot_id: str) -> dict[str, Any] | None:
    return RESULT_SNAPSHOT_SUMMARY_MAP.get(result_snapshot_id)
