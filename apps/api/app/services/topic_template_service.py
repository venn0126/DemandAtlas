from __future__ import annotations

from typing import Any


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


def list_topic_templates() -> list[dict[str, Any]]:
    return TOPIC_TEMPLATE_LIST_ITEMS


def get_topic_template(template_id: str) -> dict[str, Any] | None:
    return TOPIC_TEMPLATE_DETAIL_MAP.get(template_id)
