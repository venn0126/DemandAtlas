from __future__ import annotations

from typing import Any

from worker.pipeline.executor import build_pipeline_plan, run_pipeline
from worker.pipeline.persistence import (
    append_stage_log,
    fetch_query_task_input,
    fetch_query_task_context,
    mark_query_task_failed,
    mark_query_task_running,
    persist_result_snapshot_bundle,
)

PIPELINE_VERSION = "v1"


def execute_query_task_pipeline(query_task_id: str) -> dict[str, Any]:
    plan = build_pipeline_plan(query_task_id)

    try:
        mark_query_task_running(query_task_id)
        query_input_snapshot = fetch_query_task_input(query_task_id)
        query_task_context = fetch_query_task_context(query_task_id)
        result = run_pipeline(query_task_id, query_input_snapshot, query_task_context)

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
                stage_meta=item.get("meta"),
            )

        if result["status"] in {"success", "partial_success"}:
            result_snapshot_id = persist_result_snapshot_bundle(
                query_task_id=query_task_id,
                query_input_snapshot=query_input_snapshot,
                query_plan=result["query_plan"],
                final_status=result["status"],
                summary_stats=result["summary_stats"],
                coverage_note=result["coverage_note"],
                sync_freshness_note=result["sync_freshness_note"],
                template_snapshot={
                    "pipeline_metadata": result["pipeline_metadata"],
                    "available_boards": result["available_boards"],
                    "warnings": result["warnings"],
                },
                pipeline_version=PIPELINE_VERSION,
                clusters=result["clusters"],
                available_boards=result["available_boards"],
            )
            result["result_snapshot_id"] = result_snapshot_id
            result["current_stage"] = "snapshot"
        else:
            mark_query_task_failed(query_task_id, result["failure_reason"] or "pipeline failed")
            result["result_snapshot_id"] = None

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
