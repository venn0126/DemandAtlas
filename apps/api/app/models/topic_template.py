from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class TopicTemplate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "topic_templates"
    __table_args__ = (
        Index("ix_topic_templates_status", "status"),
    )

    code: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    default_language: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)

    versions: Mapped[list["TopicTemplateVersion"]] = relationship(back_populates="template")


class TopicTemplateVersion(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "topic_template_versions"
    __table_args__ = (
        UniqueConstraint("template_id", "version_no", name="uq_topic_template_versions_template_version"),
        Index("ix_topic_template_versions_template_id", "template_id"),
    )

    template_id: Mapped[UUID] = mapped_column(
        ForeignKey("topic_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    keywords: Mapped[dict] = mapped_column(JSONB, nullable=False)
    synonyms: Mapped[dict] = mapped_column(JSONB, nullable=False)
    exclude_terms: Mapped[dict] = mapped_column(JSONB, nullable=False)
    default_view_type: Mapped[str] = mapped_column(Text, nullable=False)
    default_sort_strategy: Mapped[str] = mapped_column(Text, nullable=False)
    config_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    template: Mapped[TopicTemplate] = relationship(back_populates="versions")
    subreddits: Mapped[list["TopicTemplateVersionSubreddit"]] = relationship(
        back_populates="template_version"
    )


class TopicTemplateVersionSubreddit(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "topic_template_version_subreddits"
    __table_args__ = (
        UniqueConstraint(
            "template_version_id",
            "subreddit_name",
            name="uq_topic_template_version_subreddits_version_subreddit",
        ),
        Index("ix_topic_template_version_subreddits_template_version_id", "template_version_id"),
        Index("ix_topic_template_version_subreddits_subreddit_name", "subreddit_name"),
    )

    template_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("topic_template_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    subreddit_name: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    template_version: Mapped[TopicTemplateVersion] = relationship(back_populates="subreddits")
