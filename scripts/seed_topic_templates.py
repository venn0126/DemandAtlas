#!/usr/bin/env python3
from __future__ import annotations

from sqlalchemy import delete, select

from app.db.session import SessionLocal
from app.models.topic_template import (
    TopicTemplate,
    TopicTemplateVersion,
    TopicTemplateVersionSubreddit,
)


SEED_ITEMS = [
    {
        "code": "tpl_ai_tools",
        "name": "AI Tools",
        "description": "AI productivity, automation, and creator tooling",
        "default_language": "en",
        "status": "active",
        "version_no": 3,
        "keywords": {"items": ["ai tools", "automation", "productivity"]},
        "synonyms": {"items": ["assistant tools", "creator tools"]},
        "exclude_terms": {"items": []},
        "default_view_type": "active",
        "default_sort_strategy": "hot",
        "config_snapshot": {"seed": True},
        "subreddits": ["ChatGPT", "OpenAI", "artificial", "productivity"],
    },
    {
        "code": "tpl_consumer_audio",
        "name": "Consumer Audio",
        "description": "Headphones, earbuds, audio accessories, and listening scenarios",
        "default_language": "en",
        "status": "active",
        "version_no": 2,
        "keywords": {"items": ["headphones", "earbuds", "audio"]},
        "synonyms": {"items": ["consumer audio"]},
        "exclude_terms": {"items": []},
        "default_view_type": "active",
        "default_sort_strategy": "hot",
        "config_snapshot": {"seed": True},
        "subreddits": ["HeadphoneAdvice", "Earbuds", "audiophile"],
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        for item in SEED_ITEMS:
            template = db.execute(
                select(TopicTemplate).where(TopicTemplate.code == item["code"])
            ).scalar_one_or_none()

            if template is None:
                template = TopicTemplate(
                    code=item["code"],
                    name=item["name"],
                    description=item["description"],
                    default_language=item["default_language"],
                    status=item["status"],
                )
                db.add(template)
                db.flush()
            else:
                template.name = item["name"]
                template.description = item["description"]
                template.default_language = item["default_language"]
                template.status = item["status"]

            version = db.execute(
                select(TopicTemplateVersion).where(
                    TopicTemplateVersion.template_id == template.id,
                    TopicTemplateVersion.version_no == item["version_no"],
                )
            ).scalar_one_or_none()

            if version is None:
                version = TopicTemplateVersion(
                    template_id=template.id,
                    version_no=item["version_no"],
                    keywords=item["keywords"],
                    synonyms=item["synonyms"],
                    exclude_terms=item["exclude_terms"],
                    default_view_type=item["default_view_type"],
                    default_sort_strategy=item["default_sort_strategy"],
                    config_snapshot=item["config_snapshot"],
                )
                db.add(version)
                db.flush()
            else:
                version.keywords = item["keywords"]
                version.synonyms = item["synonyms"]
                version.exclude_terms = item["exclude_terms"]
                version.default_view_type = item["default_view_type"]
                version.default_sort_strategy = item["default_sort_strategy"]
                version.config_snapshot = item["config_snapshot"]

            db.execute(
                delete(TopicTemplateVersionSubreddit).where(
                    TopicTemplateVersionSubreddit.template_version_id == version.id
                )
            )
            db.flush()

            for priority, subreddit_name in enumerate(item["subreddits"], start=1):
                db.add(
                    TopicTemplateVersionSubreddit(
                        template_version_id=version.id,
                        subreddit_name=subreddit_name,
                        priority=priority,
                    )
                )

        db.commit()
        print("seed_topic_templates: done")
    finally:
        db.close()


if __name__ == "__main__":
    main()
