from __future__ import annotations

import logging

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from app.core.config import settings

logger = logging.getLogger(__name__)


def enqueue_query_task_pipeline(query_task_id: str) -> bool:
    broker = RedisBroker(url=settings.redis_url)
    message = dramatiq.Message(
        queue_name="default",
        actor_name="run_query_task_pipeline",
        args=(query_task_id,),
        kwargs={},
        options={},
    )

    try:
        broker.enqueue(message)
        logger.info("enqueued query task pipeline", extra={"query_task_id": query_task_id})
        return True
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning(
            "failed to enqueue query task pipeline",
            extra={
                "query_task_id": query_task_id,
                "error": str(exc),
            },
        )
        return False
