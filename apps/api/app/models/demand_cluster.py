from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class DemandCluster(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "demand_clusters"
    __table_args__ = (
        Index("ix_demand_clusters_cluster_status", "cluster_status"),
        Index("ix_demand_clusters_last_seen_at", "last_seen_at"),
        Index("ix_demand_clusters_confidence_score", "confidence_score"),
    )

    canonical_title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    scenes: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    pain_points: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    alternatives: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    sentiment_profile: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    cluster_status: Mapped[str] = mapped_column(Text, nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    aliases: Mapped[list["DemandClusterAlias"]] = relationship(back_populates="cluster")
    metric_snapshots: Mapped[list["ClusterMetricSnapshot"]] = relationship(back_populates="cluster")
    evidences: Mapped[list["ClusterEvidence"]] = relationship(back_populates="cluster")
    snapshot_entries: Mapped[list["ResultSnapshotCluster"]] = relationship(back_populates="cluster")


class DemandClusterAlias(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "demand_cluster_aliases"
    __table_args__ = (
        UniqueConstraint("cluster_id", "alias_text", name="uq_demand_cluster_aliases_cluster_alias"),
        Index("ix_demand_cluster_aliases_cluster_id", "cluster_id"),
        Index("ix_demand_cluster_aliases_alias_text", "alias_text"),
    )

    cluster_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("demand_clusters.id", ondelete="CASCADE"),
        nullable=False,
    )
    alias_text: Mapped[str] = mapped_column(Text, nullable=False)
    alias_type: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    cluster: Mapped[DemandCluster] = relationship(back_populates="aliases")


class ClusterMetricSnapshot(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cluster_metric_snapshots"
    __table_args__ = (
        UniqueConstraint(
            "cluster_id",
            "query_task_id",
            name="uq_cluster_metric_snapshots_cluster_query_task",
        ),
        Index("ix_cluster_metric_snapshots_query_task_id", "query_task_id"),
        Index("ix_cluster_metric_snapshots_result_snapshot_id", "result_snapshot_id"),
        Index("ix_cluster_metric_snapshots_cluster_window_end", "cluster_id", "window_end"),
        Index("ix_cluster_metric_snapshots_discussion_score", "discussion_score"),
        Index("ix_cluster_metric_snapshots_growth_score", "growth_score"),
    )

    cluster_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("demand_clusters.id", ondelete="CASCADE"),
        nullable=False,
    )
    query_task_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("query_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    result_snapshot_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("result_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )
    view_type: Mapped[str] = mapped_column(Text, nullable=False)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    compare_window_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    compare_window_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    post_count: Mapped[int] = mapped_column(Integer, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, nullable=False)
    unique_user_count: Mapped[int] = mapped_column(Integer, nullable=False)
    avg_comment_depth: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    avg_post_score: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    avg_comment_score: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    high_engagement_post_ratio: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    community_spread_count: Mapped[int] = mapped_column(Integer, nullable=False)
    discussion_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    attention_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    growth_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    opportunity_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    is_weak_signal: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_low_confidence: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_emerging_signal: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    cluster: Mapped[DemandCluster] = relationship(back_populates="metric_snapshots")
    query_task: Mapped["QueryTask"] = relationship()
    result_snapshot: Mapped["ResultSnapshot"] = relationship(back_populates="metric_snapshots")


class ResultSnapshotCluster(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "result_snapshot_clusters"
    __table_args__ = (
        UniqueConstraint(
            "result_snapshot_id",
            "board_type",
            "rank_no",
            name="uq_result_snapshot_clusters_snapshot_board_rank",
        ),
        UniqueConstraint(
            "result_snapshot_id",
            "board_type",
            "cluster_id",
            name="uq_result_snapshot_clusters_snapshot_board_cluster",
        ),
        Index(
            "ix_result_snapshot_clusters_snapshot_board_rank",
            "result_snapshot_id",
            "board_type",
            "rank_no",
        ),
        Index("ix_result_snapshot_clusters_cluster_id", "cluster_id"),
    )

    result_snapshot_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("result_snapshots.id", ondelete="CASCADE"),
        nullable=False,
    )
    cluster_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("demand_clusters.id", ondelete="CASCADE"),
        nullable=False,
    )
    board_type: Mapped[str] = mapped_column(Text, nullable=False)
    rank_no: Mapped[int] = mapped_column(Integer, nullable=False)
    board_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    tie_break_meta: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    result_snapshot: Mapped["ResultSnapshot"] = relationship(back_populates="snapshot_clusters")
    cluster: Mapped[DemandCluster] = relationship(back_populates="snapshot_entries")


class ClusterEvidence(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "cluster_evidences"
    __table_args__ = (
        Index("ix_cluster_evidences_cluster_id", "cluster_id"),
        Index("ix_cluster_evidences_source_type_ref_id", "source_type", "source_ref_id"),
        Index("ix_cluster_evidences_stance", "stance"),
    )

    cluster_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("demand_clusters.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    source_ref_id: Mapped[str] = mapped_column(Text, nullable=False)
    source_internal_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    subreddit_name: Mapped[str] = mapped_column(Text, nullable=False)
    source_created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    stance: Mapped[str] = mapped_column(Text, nullable=False)
    availability_status: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    score_hint: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    cluster: Mapped[DemandCluster] = relationship(back_populates="evidences")


from app.models.query_task import QueryTask  # noqa: E402
from app.models.result_snapshot import ResultSnapshot  # noqa: E402
