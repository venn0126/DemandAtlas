from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class QueryTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "query_tasks"
    __table_args__ = (
        UniqueConstraint(
            "normalized_query_key",
            "pipeline_version",
            "view_type",
            "window_start",
            "window_end",
            name="uq_query_tasks_dedup_key",
        ),
        Index("ix_query_tasks_status_created_at", "status", "created_at"),
        Index("ix_query_tasks_user_id_created_at", "user_id", "created_at"),
        Index("ix_query_tasks_result_snapshot_id", "result_snapshot_id"),
    )

    user_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    query_type: Mapped[str] = mapped_column(Text, nullable=False)
    template_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    template_version_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    input_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    normalized_query_key: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(Text, nullable=False)
    region_hints: Mapped[dict] = mapped_column(JSONB, nullable=False)
    min_engagement_threshold: Mapped[dict] = mapped_column(JSONB, nullable=False)
    view_type: Mapped[str] = mapped_column(Text, nullable=False)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    compare_window_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    compare_window_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)
    pipeline_version: Mapped[str] = mapped_column(Text, nullable=False)
    cached_from_snapshot_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    result_snapshot_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    run_logs: Mapped[list["QueryTaskRunLog"]] = relationship(back_populates="query_task")
    result_snapshots: Mapped[list["ResultSnapshot"]] = relationship(back_populates="query_task")


class QueryTaskRunLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "query_task_run_logs"
    __table_args__ = (
        Index("ix_query_task_run_logs_query_task_id_created_at", "query_task_id", "created_at"),
        Index("ix_query_task_run_logs_stage_status", "stage", "status"),
    )

    query_task_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("query_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    stage: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    query_task: Mapped[QueryTask] = relationship(
        back_populates="run_logs",
        primaryjoin="foreign(QueryTaskRunLog.query_task_id) == QueryTask.id",
    )


from app.models.result_snapshot import ResultSnapshot  # noqa: E402
