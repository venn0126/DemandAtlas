from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.query_task_repository import (
    build_normalized_query_key,
    build_query_run_key,
    create_query_task_record,
    find_latest_query_task_by_normalized_key_prefix,
    get_query_task_by_id,
    list_query_task_run_logs,
    mark_query_task_failed_record,
    resolve_time_window,
)
from app.repositories.result_snapshot_repository import get_result_snapshot_by_id

PIPELINE_VERSION = "v1"
PIPELINE_TOTAL_STEPS = 8
PIPELINE_STAGE_ORDER = {
    "validate": 1,
    "plan": 2,
    "fetch": 3,
    "normalize": 4,
    "retrieve": 5,
    "cluster": 6,
    "score": 7,
    "snapshot": 8,
    "finalize": 8,
}


def _resolve_progress_from_logs(status: str, run_logs: list[Any], has_snapshot: bool) -> tuple[int, int, int, str | None]:
    latest_log = run_logs[-1] if run_logs else None

    if latest_log is None:
        if status == "pending":
            return 0, PIPELINE_TOTAL_STEPS, 0, None
        if has_snapshot or status in {"success", "partial_success"}:
            return PIPELINE_TOTAL_STEPS, PIPELINE_TOTAL_STEPS, 100, "snapshot"
        if status == "failed":
            return 0, PIPELINE_TOTAL_STEPS, 0, "finalize"
        return 1, PIPELINE_TOTAL_STEPS, int((1 / PIPELINE_TOTAL_STEPS) * 100), "validate"

    log_meta = latest_log.meta or {}
    total_steps = log_meta.get("total_steps") or PIPELINE_TOTAL_STEPS
    current_step = log_meta.get("current_step") or PIPELINE_STAGE_ORDER.get(latest_log.stage, 1)
    current_stage = "snapshot" if latest_log.stage == "finalize" else latest_log.stage

    if status in {"success", "partial_success"}:
        percent = 100
    elif status == "pending":
        percent = 0
    else:
        percent = int((current_step / total_steps) * 100)

    return current_step, total_steps, percent, current_stage


def _build_warning_items(
    *,
    status: str,
    failure_reason: str | None,
    coverage_note: str | None,
    run_logs: list[Any],
) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []

    if coverage_note and "partial" in coverage_note.lower():
        warnings.append(
            {
                "code": "PARTIAL_COVERAGE",
                "message": coverage_note,
            }
        )

    warnings.extend(
        {
            "code": f"PIPELINE_{log.stage.upper()}_{log.status.upper()}",
            "message": log.message,
        }
        for log in run_logs
        if log.status != "success"
    )

    if status == "failed" and failure_reason:
        warnings.append(
            {
                "code": "QUERY_TASK_FAILED",
                "message": failure_reason,
            }
        )

    unique_warnings: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in warnings:
        key = (item["code"], item["message"])
        if key in seen:
            continue
        seen.add(key)
        unique_warnings.append(item)
    return unique_warnings


def _merge_warning_items(*warning_groups: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for group in warning_groups:
        for item in group:
            key = (item["code"], item["message"])
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    return merged


def _build_cache_metadata(*, cache_source: str, freshness_seconds: int | None = None, cache_hit_query_task_id: str | None = None, cache_hit_result_snapshot_id: str | None = None, cache_hit_status: str | None = None) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "response_source": "database",
        "cache_source": cache_source,
    }
    if freshness_seconds is not None:
        meta["cache_freshness_seconds"] = freshness_seconds
    if cache_hit_query_task_id is not None:
        meta["cache_hit_query_task_id"] = cache_hit_query_task_id
    if cache_hit_result_snapshot_id is not None:
        meta["cache_hit_result_snapshot_id"] = cache_hit_result_snapshot_id
    if cache_hit_status is not None:
        meta["cache_hit_status"] = cache_hit_status
    return meta


def _build_force_refresh_metadata(query_type: str) -> dict[str, Any]:
    return {
        **_build_cache_metadata(cache_source="force_refresh_bypass"),
        "force_refresh_applied": True,
        "force_refresh_bypass_cache_lookup": True,
        "force_refresh_bypass_inflight_reuse": True,
        "force_refresh_query_type": query_type,
    }


def _snapshot_freshness_seconds(created_at: datetime | None) -> int | None:
    if created_at is None:
        return None
    now = datetime.now(UTC)
    snapshot_created_at = created_at.astimezone(UTC)
    return max(0, int((now - snapshot_created_at).total_seconds()))


def _get_cache_max_age_seconds(query_type: str) -> int:
    if query_type == "one_click":
        return settings.one_click_cache_max_age_seconds
    return settings.directed_cache_max_age_seconds


def _allow_partial_success_cache(query_type: str) -> bool:
    if query_type == "one_click":
        return settings.one_click_cache_allow_partial_success
    return settings.directed_cache_allow_partial_success


def _is_cache_fresh(query_type: str, freshness_seconds: int | None) -> bool:
    if freshness_seconds is None:
        return False
    return freshness_seconds <= _get_cache_max_age_seconds(query_type)


def _cacheable_success_statuses(query_type: str) -> tuple[str, ...]:
    return (
        ("success", "partial_success")
        if _allow_partial_success_cache(query_type)
        else ("success",)
    )


def validate_query_task_payload(payload: dict[str, Any]) -> tuple[int, dict[str, Any]] | None:
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
    return None


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

DEMO_QUERY_TASK_STATUS_BY_ID = {
    "qt_pending": "pending",
    "qt_running": "running",
    "qt_partial": "partial_success",
    "qt_success": "success",
    "qt_failed": "failed",
}


def get_demo_query_task_status_response(query_task_id: str) -> dict[str, Any] | None:
    scenario = DEMO_QUERY_TASK_STATUS_BY_ID.get(query_task_id)
    if scenario is None:
        return None

    payload = QUERY_TASK_STATUS_MAP[scenario]
    return {
        **payload,
        "data": {
            **payload["data"],
            "query_task_id": query_task_id,
        },
        "meta": {
            **payload["meta"],
            "response_source": "demo_static",
        },
    }


def create_query_task_from_db(db: Session, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    query_type = payload.get("query_type")

    validation_error = validate_query_task_payload(payload)
    if validation_error is not None:
        return validation_error

    if query_type == "one_click":
        window_start, window_end = resolve_time_window(payload, stable_preset=True)
        normalized_query_key = build_normalized_query_key(
            payload,
            query_type="one_click",
            window_start=window_start,
            window_end=window_end,
        )

        if not payload.get("force_refresh", False):
            cached_query_task = find_latest_query_task_by_normalized_key_prefix(
                db,
                normalized_query_key_prefix=normalized_query_key,
                query_type="one_click",
                pipeline_version=PIPELINE_VERSION,
                statuses=_cacheable_success_statuses("one_click"),
            )
            if (
                cached_query_task is not None
                and cached_query_task.result_snapshot_id is not None
            ):
                cache_freshness_seconds = _snapshot_freshness_seconds(cached_query_task.updated_at)
                if _is_cache_fresh("one_click", cache_freshness_seconds):
                    return (
                        200,
                        {
                            "data": {
                                "execution_mode": "cache_hit",
                                "query_task_id": str(cached_query_task.id),
                                "status": "success",
                                "result_snapshot_id": str(cached_query_task.result_snapshot_id),
                                "cached": True,
                            },
                            "meta": _build_cache_metadata(
                                cache_source="query_task_result_snapshot",
                                freshness_seconds=cache_freshness_seconds,
                                cache_hit_query_task_id=str(cached_query_task.id),
                                cache_hit_result_snapshot_id=str(cached_query_task.result_snapshot_id),
                                cache_hit_status=cached_query_task.status,
                            ),
                            "error": None,
                        },
                    )

            inflight_query_task = find_latest_query_task_by_normalized_key_prefix(
                db,
                normalized_query_key_prefix=normalized_query_key,
                query_type="one_click",
                pipeline_version=PIPELINE_VERSION,
                statuses=("pending", "running"),
            )
            if inflight_query_task is not None:
                return (
                    202,
                    {
                        "data": {
                            "execution_mode": "async",
                            "query_task_id": str(inflight_query_task.id),
                            "status": "pending",
                            "poll_url": f"/api/v1/query-tasks/{inflight_query_task.id}",
                            "anonymous_query_access_token": "anon_tok_demo",
                        },
                        "meta": {
                            **_build_cache_metadata(
                                cache_source="inflight_query_task",
                                cache_hit_query_task_id=str(inflight_query_task.id),
                            ),
                            "retry_after_ms": 1500,
                        },
                        "error": None,
                    },
                )

        query_task = create_query_task_record(
            db,
            payload=payload,
            query_type="one_click",
            status="pending",
            pipeline_version=PIPELINE_VERSION,
            window_start=window_start,
            window_end=window_end,
            normalized_query_key=build_query_run_key(normalized_query_key),
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
                    **(
                        _build_force_refresh_metadata("one_click")
                        if payload.get("force_refresh", False)
                        else _build_cache_metadata(cache_source="cache_miss")
                    ),
                    "retry_after_ms": 1500,
                },
                "error": None,
            },
        )

    window_start, window_end = resolve_time_window(payload, stable_preset=True)
    normalized_query_key = build_normalized_query_key(
        payload,
        query_type="directed",
        window_start=window_start,
        window_end=window_end,
    )

    if not payload.get("force_refresh", False):
        cached_query_task = find_latest_query_task_by_normalized_key_prefix(
            db,
            normalized_query_key_prefix=normalized_query_key,
            query_type="directed",
            pipeline_version=PIPELINE_VERSION,
            statuses=_cacheable_success_statuses("directed"),
        )
        if (
            cached_query_task is not None
            and cached_query_task.result_snapshot_id is not None
        ):
            cache_freshness_seconds = _snapshot_freshness_seconds(cached_query_task.updated_at)
            if _is_cache_fresh("directed", cache_freshness_seconds):
                return (
                    200,
                    {
                        "data": {
                            "execution_mode": "cache_hit",
                            "query_task_id": str(cached_query_task.id),
                            "status": "success",
                            "result_snapshot_id": str(cached_query_task.result_snapshot_id),
                            "cached": True,
                        },
                        "meta": _build_cache_metadata(
                            cache_source="query_task_result_snapshot",
                            freshness_seconds=cache_freshness_seconds,
                            cache_hit_query_task_id=str(cached_query_task.id),
                            cache_hit_result_snapshot_id=str(cached_query_task.result_snapshot_id),
                            cache_hit_status=cached_query_task.status,
                        ),
                        "error": None,
                    },
                )

        inflight_query_task = find_latest_query_task_by_normalized_key_prefix(
            db,
            normalized_query_key_prefix=normalized_query_key,
            query_type="directed",
            pipeline_version=PIPELINE_VERSION,
            statuses=("pending", "running"),
        )
        if inflight_query_task is not None:
            return (
                202,
                {
                    "data": {
                        "execution_mode": "async",
                        "query_task_id": str(inflight_query_task.id),
                        "status": "pending",
                        "poll_url": f"/api/v1/query-tasks/{inflight_query_task.id}",
                        "anonymous_query_access_token": "anon_tok_demo",
                    },
                    "meta": {
                        **_build_cache_metadata(
                            cache_source="inflight_query_task",
                            cache_hit_query_task_id=str(inflight_query_task.id),
                        ),
                        "retry_after_ms": 1500,
                    },
                    "error": None,
                },
            )

    query_task = create_query_task_record(
        db,
        payload=payload,
        query_type="directed",
        status="pending",
        pipeline_version=PIPELINE_VERSION,
        window_start=window_start,
        window_end=window_end,
        normalized_query_key=build_query_run_key(normalized_query_key),
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
                **(
                    _build_force_refresh_metadata("directed")
                    if payload.get("force_refresh", False)
                    else _build_cache_metadata(cache_source="cache_miss")
                ),
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

    run_logs = list_query_task_run_logs(db, query_task_uuid)
    snapshot = (
        get_result_snapshot_by_id(db, query_task.result_snapshot_id)
        if query_task.result_snapshot_id
        else None
    )
    current_step, total_steps, percent, current_stage = _resolve_progress_from_logs(
        query_task.status,
        run_logs,
        snapshot is not None,
    )
    coverage_note = snapshot.coverage_note if snapshot else None
    template_snapshot = (snapshot.template_snapshot or {}) if snapshot else {}
    pipeline_metadata = template_snapshot.get("pipeline_metadata") or {}
    snapshot_warning_items = template_snapshot.get("warnings") or []
    warnings = _merge_warning_items(
        _build_warning_items(
            status=query_task.status,
            failure_reason=query_task.failure_reason,
            coverage_note=coverage_note,
            run_logs=run_logs,
        ),
        snapshot_warning_items,
    )

    coverage_meta = pipeline_metadata.get("coverage") or {}
    source_scope_meta = pipeline_metadata.get("source_scope") or {}
    result_profile_meta = pipeline_metadata.get("result_profile") or {}

    return {
        "data": {
            "query_task_id": str(query_task.id),
            "status": query_task.status,
            "current_stage": current_stage,
            "progress": {
                "current_step": current_step,
                "total_steps": total_steps,
                "percent": percent,
            },
            "result_snapshot_id": str(query_task.result_snapshot_id) if query_task.result_snapshot_id else None,
            "coverage_note": coverage_note,
            "warnings": warnings,
        },
        "meta": {
            "response_source": "database",
            "pipeline_metadata": pipeline_metadata,
            "warning_count": len(warnings),
            "coverage_status": coverage_meta.get("status"),
            "requested_source_count": coverage_meta.get("requested_source_count"),
            "completed_source_count": coverage_meta.get("completed_source_count"),
            "source_scope_count": source_scope_meta.get("source_count"),
            "result_cluster_count": result_profile_meta.get("cluster_count"),
        },
        "error": (
            {
                "code": "QUERY_TASK_FAILED",
                "message": query_task.failure_reason or "query task failed",
                "details": {},
            }
            if query_task.status == "failed"
            else None
        ),
    }


def mark_query_task_enqueue_failed(db: Session, query_task_id: str) -> dict[str, Any] | None:
    try:
        query_task_uuid = UUID(query_task_id)
    except ValueError:
        return None

    query_task = mark_query_task_failed_record(
        db,
        query_task_id=query_task_uuid,
        failure_reason="failed to enqueue query task pipeline",
    )
    if query_task is None:
        return None

    db.commit()
    db.refresh(query_task)
    return get_query_task_status_from_db(db, str(query_task.id))
