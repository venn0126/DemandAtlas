from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Integer, MetaData, Text, column, select, table
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Session

from worker.core.db import engine


@dataclass(slots=True)
class TopicTemplateRuntime:
    template_id: str
    template_version_id: str | None
    keywords: list[str]
    synonyms: list[str]
    exclude_terms: list[str]
    candidate_subreddits: list[str]
    default_language: str
    default_view_type: str


def _normalize_str_list(value: Any) -> list[str]:
    if isinstance(value, dict):
        items = value.get("items") or value.get("terms") or []
    else:
        items = value or []
    return [
        item.strip()
        for item in items
        if isinstance(item, str) and item.strip()
    ]


def _build_template_version_public_id(template_code: str, version_no: int) -> str:
    if template_code.startswith("tpl_"):
        return f"tplv_{template_code[4:]}_{version_no:03d}"
    return f"{template_code}_v{version_no:03d}"


def _fallback_template(template_id: str) -> TopicTemplateRuntime:
    if template_id == "tpl_consumer_audio":
        return TopicTemplateRuntime(
            template_id="tpl_consumer_audio",
            template_version_id="tplv_consumer_audio_002",
            keywords=["earbuds", "headphones", "audio quality", "comfort"],
            synonyms=["wireless earbuds", "iem", "anc"],
            exclude_terms=["giveaway", "deal"],
            candidate_subreddits=["Earbuds", "HeadphoneAdvice", "headphones"],
            default_language="en",
            default_view_type="active",
        )

    return TopicTemplateRuntime(
        template_id="tpl_ai_tools",
        template_version_id="tplv_ai_tools_003",
        keywords=["ai workflow", "automation", "copilot", "prompt"],
        synonyms=["assistant", "agent", "gpt"],
        exclude_terms=["showoff", "meme"],
        candidate_subreddits=["artificial", "ChatGPT", "productivity"],
        default_language="en",
        default_view_type="active",
    )


def load_topic_template_runtime(template_id: str, template_version_id: str | None = None) -> TopicTemplateRuntime:
    try:
        _ = MetaData()
        topic_templates_table = table(
            "topic_templates",
            column("id", PGUUID(as_uuid=True)),
            column("code", Text),
            column("default_language", Text),
        )
        topic_template_versions_table = table(
            "topic_template_versions",
            column("id", PGUUID(as_uuid=True)),
            column("template_id", PGUUID(as_uuid=True)),
            column("version_no", Integer),
            column("keywords", JSONB),
            column("synonyms", JSONB),
            column("exclude_terms", JSONB),
            column("default_view_type", Text),
        )
        topic_template_version_subreddits_table = table(
            "topic_template_version_subreddits",
            column("template_version_id", PGUUID(as_uuid=True)),
            column("subreddit_name", Text),
            column("priority", Integer),
        )

        with Session(engine) as session:
            template_stmt = (
                select(
                    topic_templates_table.c.code,
                    topic_templates_table.c.default_language,
                    topic_template_versions_table.c.id,
                    topic_template_versions_table.c.version_no,
                    topic_template_versions_table.c.keywords,
                    topic_template_versions_table.c.synonyms,
                    topic_template_versions_table.c.exclude_terms,
                    topic_template_versions_table.c.default_view_type,
                )
                .join(
                    topic_template_versions_table,
                    topic_template_versions_table.c.template_id == topic_templates_table.c.id,
                )
                .where(topic_templates_table.c.code == template_id)
                .order_by(topic_template_versions_table.c.version_no.desc())
            )
            template_row = session.execute(template_stmt).first()
            if template_row is None:
                return _fallback_template(template_id)

            version_id = template_row.id
            if template_version_id and template_version_id != _build_template_version_public_id(
                template_id, template_row.version_no
            ):
                version_stmt = (
                    select(
                        topic_templates_table.c.code,
                        topic_templates_table.c.default_language,
                        topic_template_versions_table.c.id,
                        topic_template_versions_table.c.version_no,
                        topic_template_versions_table.c.keywords,
                        topic_template_versions_table.c.synonyms,
                        topic_template_versions_table.c.exclude_terms,
                        topic_template_versions_table.c.default_view_type,
                    )
                    .join(
                        topic_template_versions_table,
                        topic_template_versions_table.c.template_id == topic_templates_table.c.id,
                    )
                    .where(topic_templates_table.c.code == template_id)
                )
                for row in session.execute(version_stmt):
                    public_id = _build_template_version_public_id(template_id, row.version_no)
                    if public_id == template_version_id:
                        template_row = row
                        version_id = row.id
                        break

            subreddit_stmt = (
                select(topic_template_version_subreddits_table.c.subreddit_name)
                .where(topic_template_version_subreddits_table.c.template_version_id == version_id)
                .order_by(topic_template_version_subreddits_table.c.priority.asc())
            )
            candidate_subreddits = [row.subreddit_name for row in session.execute(subreddit_stmt)]

            return TopicTemplateRuntime(
                template_id=template_row.code,
                template_version_id=_build_template_version_public_id(
                    template_row.code,
                    template_row.version_no,
                ),
                keywords=_normalize_str_list(template_row.keywords),
                synonyms=_normalize_str_list(template_row.synonyms),
                exclude_terms=_normalize_str_list(template_row.exclude_terms),
                candidate_subreddits=candidate_subreddits,
                default_language=template_row.default_language,
                default_view_type=template_row.default_view_type,
            )
    except Exception:
        return _fallback_template(template_id)
