from __future__ import annotations

from typing import Any

from worker.pipeline.executor import build_pipeline_plan, run_pipeline
from worker.pipeline.persistence import (
    append_stage_log,
    create_result_snapshot_and_mark_success,
    fetch_query_task_input,
    mark_query_task_failed,
    mark_query_task_running,
)

PIPELINE_VERSION = "v1"


def execute_query_task_pipeline(query_task_id: str) -> dict[str, Any]:
    plan = build_pipeline_plan(query_task_id)

    try:
        mark_query_task_running(query_task_id)
        result = run_pipeline(query_task_id)

        for item in result["timeline"]:
            append_stage_log(
                query_task_id=query_task_id,
                stage=item["stage"],
                status=item["status"],
                message=item["message"],
                started_at=item["started_at"],
                finished_at=item["finished_at"],
                current_step=item["current_step"],
                total_steps=item["total_steps"],
            )

        query_input_snapshot = fetch_query_task_input(query_task_id)
        result_snapshot_id = create_result_snapshot_and_mark_success(
            query_task_id=query_task_id,
            query_input_snapshot=query_input_snapshot,
            pipeline_version=PIPELINE_VERSION,
        )
        result["result_snapshot_id"] = result_snapshot_id
        result["current_stage"] = "snapshot"

        return {
            "plan": plan,
            "result": result,
        }
    except Exception as exc:  # pragma: no cover - defensive runtime path
        mark_query_task_failed(query_task_id, str(exc))
        return {
            "plan": plan,
            "result": {
                "query_task_id": query_task_id,
                "status": "failed",
                "current_stage": "finalize",
                "progress": {
                    "current_step": 0,
                    "total_steps": 8,
                    "percent": 0,
                },
                "timeline": [],
                "result_snapshot_id": None,
                "coverage_note": None,
                "warnings": [],
                "failure_reason": str(exc),
            },
        }
