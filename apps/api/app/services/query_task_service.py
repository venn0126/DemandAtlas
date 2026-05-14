from __future__ import annotations

from uuid import UUID
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.query_task_repository import (
    create_query_task_record,
    create_result_snapshot_record,
    get_query_task_by_id,
)

PIPELINE_VERSION = "v1"


def create_query_task_response(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    query_type = payload.get("query_type")

    if query_type == "directed" and len(payload.get("keywords", [])) > 3:
        return (
            422,
            {
                "data": None,
                "meta": {},
                "error": {
                    "code": "QUERY_TOO_BROAD",
                    "message": "query scope is too broad for V1 execution limits",
                    "details": {
                        "max_keywords": 5,
                        "max_subreddits": 20,
                    },
                },
            },
        )

    if query_type == "one_click":
        return (
            200,
            {
                "data": {
                    "execution_mode": "cache_hit",
                    "query_task_id": "qt_01JVA1HBM4YF2T2M6Q5M5M2F0A",
                    "status": "success",
                    "result_snapshot_id": "rs_01JVA1JD7YQCKRZVMD0W2X5P4M",
                    "cached": True,
                },
                "meta": {},
                "error": None,
            },
        )

    return (
        202,
        {
            "data": {
                "execution_mode": "async",
                "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
                "status": "pending",
                "poll_url": "/api/v1/query-tasks/qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
                "anonymous_query_access_token": "anon_tok_demo",
            },
            "meta": {
                "retry_after_ms": 1500,
            },
            "error": None,
        },
    )


QUERY_TASK_STATUS_MAP: dict[str, dict[str, Any]] = {
    "pending": {
        "data": {
            "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
            "status": "pending",
            "current_stage": None,
            "progress": {
                "current_step": 0,
                "total_steps": 8,
                "percent": 0,
            },
            "result_snapshot_id": None,
            "coverage_note": None,
            "warnings": [],
        },
        "meta": {},
        "error": None,
    },
    "running": {
        "data": {
            "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
            "status": "running",
            "current_stage": "cluster",
            "progress": {
                "current_step": 6,
                "total_steps": 8,
                "percent": 72,
            },
            "result_snapshot_id": None,
            "coverage_note": None,
            "warnings": [],
        },
        "meta": {},
        "error": None,
    },
    "partial_success": {
        "data": {
            "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
            "status": "partial_success",
            "current_stage": "snapshot",
            "progress": {
                "current_step": 8,
                "total_steps": 8,
                "percent": 100,
            },
            "result_snapshot_id": "rs_01JVA1PAB2Y9PGKQ7NH1AK6R9M",
            "coverage_note": "2 candidate subreddits failed during fetch; results were generated from available sources",
            "warnings": [
                {
                    "code": "PARTIAL_FETCH_FAILURE",
                    "message": "some subreddit data was unavailable",
                }
            ],
        },
        "meta": {},
        "error": None,
    },
    "success": {
        "data": {
            "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
            "status": "success",
            "current_stage": "snapshot",
            "progress": {
                "current_step": 8,
                "total_steps": 8,
                "percent": 100,
            },
            "result_snapshot_id": "rs_01JVA1T4WM4B3PG5N8W1HEP7QA",
            "coverage_note": "full coverage on candidate sources",
            "warnings": [],
        },
        "meta": {},
        "error": None,
    },
    "failed": {
        "data": {
            "query_task_id": "qt_01JVA1M1WEX6NQ0QJQYY23H5Q8",
            "status": "failed",
            "current_stage": "fetch",
            "progress": {
                "current_step": 3,
                "total_steps": 8,
                "percent": 25,
            },
            "result_snapshot_id": None,
            "coverage_note": None,
            "warnings": [],
        },
        "meta": {},
        "error": {
            "code": "NO_FETCHABLE_SOURCE",
            "message": "unable to fetch any valid source data",
            "details": {},
        },
    },
}


def get_query_task_status_response(status: str) -> dict[str, Any]:
    return QUERY_TASK_STATUS_MAP[status]


def create_query_task_from_db(db: Session, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    query_type = payload.get("query_type")

    if query_type == "directed" and len(payload.get("keywords", [])) > 3:
        return create_query_task_response(payload)

    if query_type == "one_click":
        query_task = create_query_task_record(
            db,
            payload=payload,
            query_type="one_click",
            status="success",
            pipeline_version=PIPELINE_VERSION,
        )
        snapshot = create_result_snapshot_record(
            db,
            query_task_id=query_task.id,
            payload=payload,
            summary_stats={"cluster_count": 11, "post_count": 141, "comment_count": 1094},
            coverage_note="cache hit placeholder result",
            sync_freshness_note="latest source sync at placeholder time",
            pipeline_version=PIPELINE_VERSION,
        )
        query_task.result_snapshot_id = snapshot.id
        query_task.cached_from_snapshot_id = snapshot.id
        db.commit()
        db.refresh(query_task)

        return (
            200,
            {
                "data": {
                    "execution_mode": "cache_hit",
                    "query_task_id": str(query_task.id),
                    "status": "success",
                    "result_snapshot_id": str(snapshot.id),
                    "cached": True,
                },
                "meta": {},
                "error": None,
            },
        )

    query_task = create_query_task_record(
        db,
        payload=payload,
        query_type="directed",
        status="pending",
        pipeline_version=PIPELINE_VERSION,
    )
    db.commit()
    db.refresh(query_task)

    return (
        202,
        {
            "data": {
                "execution_mode": "async",
                "query_task_id": str(query_task.id),
                "status": "pending",
                "poll_url": f"/api/v1/query-tasks/{query_task.id}",
                "anonymous_query_access_token": "anon_tok_demo",
            },
            "meta": {
                "retry_after_ms": 1500,
            },
            "error": None,
        },
    )


def get_query_task_status_from_db(db: Session, query_task_id: str) -> dict[str, Any] | None:
    try:
        query_task_uuid = UUID(query_task_id)
    except ValueError:
        return None

    query_task = get_query_task_by_id(db, query_task_uuid)
    if query_task is None:
        return None

    progress_map = {
        "pending": {"current_step": 0, "total_steps": 8, "percent": 0},
        "running": {"current_step": 4, "total_steps": 8, "percent": 50},
        "partial_success": {"current_step": 8, "total_steps": 8, "percent": 100},
        "success": {"current_step": 8, "total_steps": 8, "percent": 100},
        "failed": {"current_step": 3, "total_steps": 8, "percent": 25},
    }

    return {
        "data": {
            "query_task_id": str(query_task.id),
            "status": query_task.status,
            "current_stage": "snapshot" if query_task.status in {"success", "partial_success"} else None,
            "progress": progress_map.get(query_task.status, progress_map["running"]),
            "result_snapshot_id": str(query_task.result_snapshot_id) if query_task.result_snapshot_id else None,
            "coverage_note": None,
            "warnings": [],
        },
        "meta": {},
        "error": None,
    }
