from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, MetaData, Text, column, select, table, update
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

from worker.core.db import engine

metadata = MetaData()

query_tasks_table = table(
    "query_tasks",
    column("id", PGUUID(as_uuid=True)),
    column("status", Text),
    column("started_at", DateTime(timezone=True)),
    column("updated_at", DateTime(timezone=True)),
    column("finished_at", DateTime(timezone=True)),
    column("failure_reason", Text),
    column("result_snapshot_id", PGUUID(as_uuid=True)),
    column("input_payload", JSONB),
)

query_task_run_logs_table = table(
    "query_task_run_logs",
    column("id", PGUUID(as_uuid=True)),
    column("query_task_id", PGUUID(as_uuid=True)),
    column("stage", Text),
    column("status", Text),
    column("message", Text),
    column("meta", JSONB),
    column("started_at", DateTime(timezone=True)),
    column("finished_at", DateTime(timezone=True)),
    column("created_at", DateTime(timezone=True)),
)

result_snapshots_table = table(
    "result_snapshots",
    column("id", PGUUID(as_uuid=True)),
    column("query_task_id", PGUUID(as_uuid=True)),
    column("query_input_snapshot", JSONB),
    column("template_snapshot", JSONB),
    column("summary_stats", JSONB),
    column("coverage_note", Text),
    column("sync_freshness_note", Text),
    column("pipeline_version", Text),
    column("generated_at", DateTime(timezone=True)),
    column("created_at", DateTime(timezone=True)),
    column("updated_at", DateTime(timezone=True)),
)


def utc_now() -> datetime:
    return datetime.now(UTC)


def to_uuid(value: str) -> UUID:
    return UUID(value)


def mark_query_task_running(query_task_id: str) -> None:
    stmt = (
        update(query_tasks_table)
        .where(query_tasks_table.c.id == to_uuid(query_task_id))
        .values(
            status="running",
            started_at=utc_now(),
            updated_at=utc_now(),
        )
    )
    with engine.begin() as connection:
        connection.execute(stmt)


def fetch_query_task_input(query_task_id: str) -> dict:
    stmt = select(query_tasks_table.c.input_payload).where(
        query_tasks_table.c.id == to_uuid(query_task_id)
    )
    with engine.begin() as connection:
        row = connection.execute(stmt).one()
    return row[0] or {}


def append_stage_log(
    *,
    query_task_id: str,
    stage: str,
    status: str,
    message: str,
    started_at: str,
    finished_at: str,
    current_step: int,
    total_steps: int,
    stage_meta: dict | None = None,
) -> None:
    stmt = query_task_run_logs_table.insert().values(
        id=uuid4(),
        query_task_id=to_uuid(query_task_id),
        stage=stage,
        status=status,
        message=message,
        meta={
            "current_step": current_step,
            "total_steps": total_steps,
            **(stage_meta or {}),
        },
        started_at=datetime.fromisoformat(started_at),
        finished_at=datetime.fromisoformat(finished_at),
        created_at=utc_now(),
    )
    with engine.begin() as connection:
        connection.execute(stmt)


def create_result_snapshot_and_mark_completion(
    *,
    query_task_id: str,
    query_input_snapshot: dict,
    final_status: str,
    summary_stats: dict,
    coverage_note: str | None,
    sync_freshness_note: str | None,
    template_snapshot: dict | None,
    pipeline_version: str,
) -> str:
    result_snapshot_uuid = uuid4()

    update_query_task = (
        update(query_tasks_table)
        .where(query_tasks_table.c.id == to_uuid(query_task_id))
        .values(
            status=final_status,
            result_snapshot_id=result_snapshot_uuid,
            finished_at=utc_now(),
            updated_at=utc_now(),
        )
    )

    with engine.begin() as connection:
        connection.execute(
            result_snapshots_table.insert().values(
                id=result_snapshot_uuid,
                query_task_id=to_uuid(query_task_id),
                query_input_snapshot=query_input_snapshot,
                template_snapshot=template_snapshot,
                summary_stats=summary_stats,
                coverage_note=coverage_note,
                sync_freshness_note=sync_freshness_note,
                pipeline_version=pipeline_version,
                generated_at=utc_now(),
                created_at=utc_now(),
                updated_at=utc_now(),
            )
        )
        connection.execute(update_query_task)

    return str(result_snapshot_uuid)


def mark_query_task_failed(query_task_id: str, failure_reason: str) -> None:
    stmt = (
        update(query_tasks_table)
        .where(query_tasks_table.c.id == to_uuid(query_task_id))
        .values(
            status="failed",
            failure_reason=failure_reason,
            finished_at=utc_now(),
            updated_at=utc_now(),
        )
    )
    with engine.begin() as connection:
        connection.execute(stmt)
