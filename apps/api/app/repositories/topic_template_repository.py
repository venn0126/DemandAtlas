from __future__ import annotations

from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.topic_template import (
    TopicTemplate,
    TopicTemplateVersion,
    TopicTemplateVersionSubreddit,
)


def _build_template_version_public_id(template_code: str, version_no: int) -> str:
    if template_code.startswith("tpl_"):
        return f"tplv_{template_code[4:]}_{version_no:03d}"
    return f"{template_code}_v{version_no:03d}"


def _latest_version_subquery() -> Select:
    return (
        select(
            TopicTemplateVersion.template_id.label("template_id"),
            func.max(TopicTemplateVersion.version_no).label("latest_version_no"),
        )
        .group_by(TopicTemplateVersion.template_id)
        .subquery()
    )


def list_active_topic_templates(db: Session) -> list[dict[str, Any]]:
    latest_version = _latest_version_subquery()

    stmt = (
        select(
            TopicTemplate.code,
            TopicTemplate.name,
            TopicTemplate.description,
            TopicTemplate.default_language,
            TopicTemplateVersion.version_no,
            TopicTemplateVersion.default_view_type,
        )
        .join(latest_version, latest_version.c.template_id == TopicTemplate.id)
        .join(
            TopicTemplateVersion,
            (TopicTemplateVersion.template_id == TopicTemplate.id)
            & (TopicTemplateVersion.version_no == latest_version.c.latest_version_no),
        )
        .where(TopicTemplate.status == "active")
        .order_by(TopicTemplate.name.asc())
    )

    rows = db.execute(stmt).all()
    return [
        {
            "template_id": row.code,
            "template_version_id": _build_template_version_public_id(row.code, row.version_no),
            "name": row.name,
            "description": row.description,
            "default_language": row.default_language,
            "default_view_type": row.default_view_type,
        }
        for row in rows
    ]


def get_topic_template_by_code(db: Session, template_code: str) -> dict[str, Any] | None:
    latest_version = _latest_version_subquery()

    stmt = (
        select(
            TopicTemplate.code,
            TopicTemplate.name,
            TopicTemplate.description,
            TopicTemplate.default_language,
            TopicTemplateVersion.version_no,
            TopicTemplateVersion.default_view_type,
            func.count(TopicTemplateVersionSubreddit.id).label("candidate_subreddit_count"),
        )
        .join(latest_version, latest_version.c.template_id == TopicTemplate.id)
        .join(
            TopicTemplateVersion,
            (TopicTemplateVersion.template_id == TopicTemplate.id)
            & (TopicTemplateVersion.version_no == latest_version.c.latest_version_no),
        )
        .outerjoin(
            TopicTemplateVersionSubreddit,
            TopicTemplateVersionSubreddit.template_version_id == TopicTemplateVersion.id,
        )
        .where(TopicTemplate.code == template_code)
        .group_by(
            TopicTemplate.code,
            TopicTemplate.name,
            TopicTemplate.description,
            TopicTemplate.default_language,
            TopicTemplateVersion.version_no,
            TopicTemplateVersion.default_view_type,
        )
    )

    row = db.execute(stmt).one_or_none()
    if row is None:
        return None

    return {
        "template_id": row.code,
        "template_version_id": _build_template_version_public_id(row.code, row.version_no),
        "name": row.name,
        "description": row.description,
        "default_language": row.default_language,
        "default_view_type": row.default_view_type,
        "candidate_subreddit_count": row.candidate_subreddit_count,
    }
