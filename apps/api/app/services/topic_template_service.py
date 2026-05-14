from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.repositories.topic_template_repository import (
    get_topic_template_by_code,
    list_active_topic_templates,
)

logger = logging.getLogger(__name__)


TOPIC_TEMPLATE_LIST_ITEMS: list[dict[str, Any]] = [
    {
        "template_id": "tpl_ai_tools",
        "template_version_id": "tplv_ai_tools_003",
        "name": "AI Tools",
        "description": "AI productivity, automation, and creator tooling",
        "default_language": "en",
        "default_view_type": "active",
    },
    {
        "template_id": "tpl_consumer_audio",
        "template_version_id": "tplv_consumer_audio_002",
        "name": "Consumer Audio",
        "description": "Headphones, earbuds, audio accessories, and listening scenarios",
        "default_language": "en",
        "default_view_type": "active",
    },
]

TOPIC_TEMPLATE_DETAIL_MAP: dict[str, dict[str, Any]] = {
    "tpl_ai_tools": {
        "template_id": "tpl_ai_tools",
        "template_version_id": "tplv_ai_tools_003",
        "name": "AI Tools",
        "description": "AI productivity, automation, and creator tooling",
        "default_language": "en",
        "default_view_type": "active",
        "candidate_subreddit_count": 12,
    },
    "tpl_consumer_audio": {
        "template_id": "tpl_consumer_audio",
        "template_version_id": "tplv_consumer_audio_002",
        "name": "Consumer Audio",
        "description": "Headphones, earbuds, audio accessories, and listening scenarios",
        "default_language": "en",
        "default_view_type": "active",
        "candidate_subreddit_count": 8,
    },
}


def list_topic_templates(db: Session | None = None) -> list[dict[str, Any]]:
    if db is None:
        return TOPIC_TEMPLATE_LIST_ITEMS

    try:
        items = list_active_topic_templates(db)
        return items or TOPIC_TEMPLATE_LIST_ITEMS
    except Exception as exc:  # pragma: no cover - fallback path
        logger.warning("list_topic_templates fallback to static data: %s", exc)
        return TOPIC_TEMPLATE_LIST_ITEMS


def get_topic_template(template_id: str, db: Session | None = None) -> dict[str, Any] | None:
    if db is None:
        return TOPIC_TEMPLATE_DETAIL_MAP.get(template_id)

    try:
        template = get_topic_template_by_code(db, template_id)
        return template or TOPIC_TEMPLATE_DETAIL_MAP.get(template_id)
    except Exception as exc:  # pragma: no cover - fallback path
        logger.warning("get_topic_template fallback to static data: %s", exc)
        return TOPIC_TEMPLATE_DETAIL_MAP.get(template_id)
