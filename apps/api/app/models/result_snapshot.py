from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ResultSnapshot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "result_snapshots"
    __table_args__ = (
        UniqueConstraint("query_task_id", name="uq_result_snapshots_query_task_id"),
        Index("ix_result_snapshots_generated_at", "generated_at"),
    )

    query_task_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("query_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    query_input_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    template_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    summary_stats: Mapped[dict] = mapped_column(JSONB, nullable=False)
    coverage_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    sync_freshness_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    pipeline_version: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    query_task: Mapped["QueryTask"] = relationship(
        back_populates="result_snapshots",
        primaryjoin="foreign(ResultSnapshot.query_task_id) == QueryTask.id",
    )


from app.models.query_task import QueryTask  # noqa: E402
