from fastapi import APIRouter

from app.api.v1.routes.health import router as health_router
from app.api.v1.routes.query_task_status import router as query_task_status_router
from app.api.v1.routes.query_tasks import router as query_tasks_router
from app.api.v1.routes.result_snapshots import router as result_snapshots_router
from app.api.v1.routes.topic_templates import router as topic_templates_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(query_tasks_router)
api_router.include_router(query_task_status_router)
api_router.include_router(result_snapshots_router)
api_router.include_router(topic_templates_router)
