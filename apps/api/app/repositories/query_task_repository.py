from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.query_task import QueryTask, QueryTaskRunLog
from app.models.result_snapshot import ResultSnapshot


def resolve_time_window(payload: dict, *, stable_preset: bool = False) -> tuple[datetime, datetime]:
    time_window = payload.get("time_window", {})

    if "start_at" in time_window and "end_at" in time_window:
        return (
            datetime.fromisoformat(time_window["start_at"].replace("Z", "+00:00")),
            datetime.fromisoformat(time_window["end_at"].replace("Z", "+00:00")),
        )

    preset = time_window.get("preset", "30d")
    days = {"7d": 7, "30d": 30, "90d": 90}.get(preset, 30)
    end_at = datetime.now(UTC)
    if stable_preset:
        end_at = end_at.replace(hour=0, minute=0, second=0, microsecond=0)
    start_at = end_at - timedelta(days=days)
    return start_at, end_at


def build_normalized_query_key(
    payload: dict,
    *,
    query_type: str,
    window_start: datetime,
    window_end: datetime,
) -> str:
    base_payload: dict[str, object] = {
        "query_type": query_type,
        "view_type": payload.get("view_type") or "active",
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
    }

    if query_type == "one_click":
        base_payload["template_id"] = payload.get("template_id")
        base_payload["template_version_id"] = payload.get("template_version_id")
    else:
        base_payload["keywords"] = sorted(
            item.strip().lower()
            for item in payload.get("keywords", [])
            if isinstance(item, str) and item.strip()
        )
        base_payload["subreddits"] = sorted(
            item.strip().lower()
            for item in payload.get("subreddits", [])
            if isinstance(item, str) and item.strip()
        )
        base_payload["language"] = payload.get("language", "en")
        base_payload["region_hints"] = sorted(
            item.strip().lower()
            for item in payload.get("region_hints", [])
            if isinstance(item, str) and item.strip()
        )
        base_payload["min_engagement_threshold"] = payload.get("min_engagement_threshold") or {}

    return json.dumps(base_payload, sort_keys=True, separators=(",", ":"))


def build_query_run_key(normalized_query_key: str) -> str:
    return f"{normalized_query_key}#run:{uuid4().hex}"


def create_query_task_record(
    db: Session,
    *,
    payload: dict,
    query_type: str,
    status: str,
    pipeline_version: str,
    window_start: datetime | None = None,
    window_end: datetime | None = None,
    normalized_query_key: str | None = None,
    result_snapshot_id: UUID | None = None,
    failure_reason: str | None = None,
) -> QueryTask:
    resolved_window_start = window_start
    resolved_window_end = window_end
    if resolved_window_start is None or resolved_window_end is None:
        resolved_window_start, resolved_window_end = resolve_time_window(payload)

    resolved_normalized_query_key = normalized_query_key or build_normalized_query_key(
        payload,
        query_type=query_type,
        window_start=resolved_window_start,
        window_end=resolved_window_end,
    )

    query_task = QueryTask(
        user_id=None,
        query_type=query_type,
        template_id=None,
        template_version_id=None,
        input_payload=payload,
        normalized_query_key=resolved_normalized_query_key,
        language=payload.get("language", "en"),
        region_hints={"items": payload.get("region_hints", [])},
        min_engagement_threshold=payload.get("min_engagement_threshold") or {},
        view_type=payload.get("view_type") or "active",
        window_start=resolved_window_start,
        window_end=resolved_window_end,
        compare_window_start=None,
        compare_window_end=None,
        status=status,
        pipeline_version=pipeline_version,
        cached_from_snapshot_id=result_snapshot_id,
        result_snapshot_id=result_snapshot_id,
        failure_reason=failure_reason,
        started_at=datetime.now(UTC) if status != "pending" else None,
        finished_at=datetime.now(UTC) if status in {"success", "failed"} else None,
    )
    db.add(query_task)
    db.flush()
    return query_task


def create_result_snapshot_record(
    db: Session,
    *,
    query_task_id: UUID,
    payload: dict,
    summary_stats: dict,
    coverage_note: str | None,
    sync_freshness_note: str | None,
    pipeline_version: str,
) -> ResultSnapshot:
    snapshot = ResultSnapshot(
        query_task_id=query_task_id,
        query_input_snapshot=payload,
        template_snapshot=None,
        summary_stats=summary_stats,
        coverage_note=coverage_note,
        sync_freshness_note=sync_freshness_note,
        pipeline_version=pipeline_version,
        generated_at=datetime.now(UTC),
    )
    db.add(snapshot)
    db.flush()
    return snapshot


def get_query_task_by_id(db: Session, query_task_id: UUID) -> QueryTask | None:
    return db.get(QueryTask, query_task_id)


def find_latest_query_task_by_normalized_key_prefix(
    db: Session,
    *,
    normalized_query_key_prefix: str,
    query_type: str,
    pipeline_version: str,
    statuses: tuple[str, ...] | None = None,
) -> QueryTask | None:
    stmt = (
        select(QueryTask)
        .where(QueryTask.query_type == query_type)
        .where(QueryTask.pipeline_version == pipeline_version)
        .where(QueryTask.normalized_query_key.startswith(normalized_query_key_prefix))
        .order_by(QueryTask.created_at.desc())
    )
    if statuses:
        stmt = stmt.where(QueryTask.status.in_(statuses))
    return db.scalar(stmt)


def list_query_task_run_logs(db: Session, query_task_id: UUID) -> list[QueryTaskRunLog]:
    stmt = (
        select(QueryTaskRunLog)
        .where(QueryTaskRunLog.query_task_id == query_task_id)
        .order_by(QueryTaskRunLog.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def mark_query_task_failed_record(
    db: Session,
    *,
    query_task_id: UUID,
    failure_reason: str,
) -> QueryTask | None:
    query_task = db.get(QueryTask, query_task_id)
    if query_task is None:
        return None

    now = datetime.now(UTC)
    query_task.status = "failed"
    query_task.failure_reason = failure_reason
    query_task.finished_at = now
    query_task.updated_at = now
    db.flush()
    return query_task
