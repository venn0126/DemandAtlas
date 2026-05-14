from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from worker.pipeline.stages import FINALIZING_STAGE, PIPELINE_STAGES


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_pipeline_plan(query_task_id: str) -> dict[str, Any]:
    return {
        "query_task_id": query_task_id,
        "pipeline_stages": list(PIPELINE_STAGES),
        "finalize_stage": FINALIZING_STAGE,
        "created_at": utc_now_iso(),
    }


def run_pipeline(query_task_id: str) -> dict[str, Any]:
    timeline: list[dict[str, Any]] = []

    for index, stage in enumerate(PIPELINE_STAGES, start=1):
        timeline.append(
            {
                "stage": stage,
                "status": "success",
                "started_at": utc_now_iso(),
                "finished_at": utc_now_iso(),
                "current_step": index,
                "total_steps": len(PIPELINE_STAGES),
                "message": f"{stage} stage completed in placeholder mode",
            }
        )

    timeline.append(
        {
            "stage": FINALIZING_STAGE,
            "status": "success",
            "started_at": utc_now_iso(),
            "finished_at": utc_now_iso(),
            "current_step": len(PIPELINE_STAGES),
            "total_steps": len(PIPELINE_STAGES),
            "message": "pipeline finalized in placeholder mode",
        }
    )

    return {
        "query_task_id": query_task_id,
        "status": "success",
        "current_stage": FINALIZING_STAGE,
        "progress": {
            "current_step": len(PIPELINE_STAGES),
            "total_steps": len(PIPELINE_STAGES),
            "percent": 100,
        },
        "timeline": timeline,
        "result_snapshot_id": None,
        "coverage_note": None,
        "warnings": [],
    }
