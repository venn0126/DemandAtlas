from __future__ import annotations

import dramatiq

from worker.pipeline.executor import build_pipeline_plan, run_pipeline


@dramatiq.actor
def run_query_task_pipeline(query_task_id: str) -> dict:
    plan = build_pipeline_plan(query_task_id)
    result = run_pipeline(query_task_id)

    return {
        "plan": plan,
        "result": result,
    }
