from __future__ import annotations

import dramatiq

from worker.services.query_task_pipeline_service import execute_query_task_pipeline


@dramatiq.actor
def run_query_task_pipeline(query_task_id: str) -> dict:
    return execute_query_task_pipeline(query_task_id)
