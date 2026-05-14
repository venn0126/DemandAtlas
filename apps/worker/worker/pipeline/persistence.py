from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import MetaData, Table, column, select, table, update

from worker.core.db import engine

metadata = MetaData()

query_tasks = Table("query_tasks", metadata)
query_task_run_logs = Table("query_task_run_logs", metadata)
result_snapshots = Table("result_snapshots", metadata)


def utc_now() -> datetime:
    return datetime.now(UTC)


def mark_query_task_running(query_task_id: str) -> None:
    stmt = (
        update(table("query_tasks", column("id"), column("status"), column("started_at"), column("updated_at")))
        .where(column("id") == query_task_id)
        .values(
            status="running",
            started_at=utc_now(),
            updated_at=utc_now(),
        )
    )
    with engine.begin() as connection:
        connection.execute(stmt)


def fetch_query_task_input(query_task_id: str) -> dict:
    stmt = select(column("input_payload")).select_from(
        table("query_tasks", column("id"), column("input_payload"))
    ).where(column("id") == query_task_id)
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
) -> None:
    log_table = table(
        "query_task_run_logs",
        column("id"),
        column("query_task_id"),
        column("stage"),
        column("status"),
        column("message"),
        column("meta"),
        column("started_at"),
        column("finished_at"),
        column("created_at"),
    )

    stmt = log_table.insert().values(
        id=uuid4(),
        query_task_id=query_task_id,
        stage=stage,
        status=status,
        message=message,
        meta={
            "current_step": current_step,
            "total_steps": total_steps,
        },
        started_at=datetime.fromisoformat(started_at),
        finished_at=datetime.fromisoformat(finished_at),
        created_at=utc_now(),
    )
    with engine.begin() as connection:
        connection.execute(stmt)


def create_result_snapshot_and_mark_success(
    *,
    query_task_id: str,
    query_input_snapshot: dict,
    pipeline_version: str,
) -> str:
    result_snapshot_id = str(uuid4())

    snapshot_table = table(
        "result_snapshots",
        column("id"),
        column("query_task_id"),
        column("query_input_snapshot"),
        column("template_snapshot"),
        column("summary_stats"),
        column("coverage_note"),
        column("sync_freshness_note"),
        column("pipeline_version"),
        column("generated_at"),
        column("created_at"),
        column("updated_at"),
    )

    update_query_task = (
        update(
            table(
                "query_tasks",
                column("id"),
                column("status"),
                column("result_snapshot_id"),
                column("finished_at"),
                column("updated_at"),
            )
        )
        .where(column("id") == query_task_id)
        .values(
            status="success",
            result_snapshot_id=result_snapshot_id,
            finished_at=utc_now(),
            updated_at=utc_now(),
        )
    )

    with engine.begin() as connection:
        connection.execute(
            snapshot_table.insert().values(
                id=result_snapshot_id,
                query_task_id=query_task_id,
                query_input_snapshot=query_input_snapshot,
                template_snapshot=None,
                summary_stats={
                    "cluster_count": 1,
                    "post_count": 1,
                    "comment_count": 1,
                },
                coverage_note="placeholder worker pipeline completed",
                sync_freshness_note="placeholder sync freshness note",
                pipeline_version=pipeline_version,
                generated_at=utc_now(),
                created_at=utc_now(),
                updated_at=utc_now(),
            )
        )
        connection.execute(update_query_task)

    return result_snapshot_id


def mark_query_task_failed(query_task_id: str, failure_reason: str) -> None:
    stmt = (
        update(
            table(
                "query_tasks",
                column("id"),
                column("status"),
                column("failure_reason"),
                column("finished_at"),
                column("updated_at"),
            )
        )
        .where(column("id") == query_task_id)
        .values(
            status="failed",
            failure_reason=failure_reason,
            finished_at=utc_now(),
            updated_at=utc_now(),
        )
    )
    with engine.begin() as connection:
        connection.execute(stmt)
