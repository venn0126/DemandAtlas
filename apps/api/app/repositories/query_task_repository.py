from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.query_task import QueryTask
from app.models.result_snapshot import ResultSnapshot


def _resolve_time_window(payload: dict) -> tuple[datetime, datetime]:
    time_window = payload.get("time_window", {})

    if "start_at" in time_window and "end_at" in time_window:
        return (
            datetime.fromisoformat(time_window["start_at"].replace("Z", "+00:00")),
            datetime.fromisoformat(time_window["end_at"].replace("Z", "+00:00")),
        )

    preset = time_window.get("preset", "30d")
    days = {"7d": 7, "30d": 30, "90d": 90}.get(preset, 30)
    end_at = datetime.now(UTC)
    start_at = end_at - timedelta(days=days)
    return start_at, end_at


def create_query_task_record(
    db: Session,
    *,
    payload: dict,
    query_type: str,
    status: str,
    pipeline_version: str,
    result_snapshot_id: UUID | None = None,
    failure_reason: str | None = None,
) -> QueryTask:
    window_start, window_end = _resolve_time_window(payload)

    query_task = QueryTask(
        user_id=None,
        query_type=query_type,
        template_id=None,
        template_version_id=None,
        input_payload=payload,
        normalized_query_key=f"{query_type}:{window_start.isoformat()}:{window_end.isoformat()}",
        language=payload.get("language", "en"),
        region_hints={"items": payload.get("region_hints", [])},
        min_engagement_threshold=payload.get("min_engagement_threshold") or {},
        view_type=payload.get("view_type") or "active",
        window_start=window_start,
        window_end=window_end,
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
