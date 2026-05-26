"""add sprint 02 result tables

Revision ID: 20260519_02
Revises: 20260514_01
Create Date: 2026-05-19 15:20:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260519_02"
down_revision = "20260514_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "demand_clusters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("canonical_title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("scenes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("pain_points", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("alternatives", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("sentiment_profile", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("cluster_status", sa.Text(), nullable=False),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_demand_clusters_cluster_status", "demand_clusters", ["cluster_status"])
    op.create_index("ix_demand_clusters_last_seen_at", "demand_clusters", ["last_seen_at"])
    op.create_index("ix_demand_clusters_confidence_score", "demand_clusters", ["confidence_score"])

    op.create_table(
        "demand_cluster_aliases",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cluster_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("alias_text", sa.Text(), nullable=False),
        sa.Column("alias_type", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["cluster_id"], ["demand_clusters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cluster_id", "alias_text", name="uq_demand_cluster_aliases_cluster_alias"),
    )
    op.create_index("ix_demand_cluster_aliases_cluster_id", "demand_cluster_aliases", ["cluster_id"])
    op.create_index("ix_demand_cluster_aliases_alias_text", "demand_cluster_aliases", ["alias_text"])

    op.create_table(
        "cluster_metric_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cluster_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("result_snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("view_type", sa.Text(), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("compare_window_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("compare_window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("post_count", sa.Integer(), nullable=False),
        sa.Column("comment_count", sa.Integer(), nullable=False),
        sa.Column("unique_user_count", sa.Integer(), nullable=False),
        sa.Column("avg_comment_depth", sa.Numeric(8, 2), nullable=False),
        sa.Column("avg_post_score", sa.Numeric(10, 2), nullable=False),
        sa.Column("avg_comment_score", sa.Numeric(10, 2), nullable=False),
        sa.Column("high_engagement_post_ratio", sa.Numeric(5, 2), nullable=False),
        sa.Column("community_spread_count", sa.Integer(), nullable=False),
        sa.Column("discussion_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("attention_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("growth_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("opportunity_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("is_weak_signal", sa.Boolean(), nullable=False),
        sa.Column("is_low_confidence", sa.Boolean(), nullable=False),
        sa.Column("is_emerging_signal", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["cluster_id"], ["demand_clusters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["query_task_id"], ["query_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["result_snapshot_id"], ["result_snapshots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cluster_id", "query_task_id", name="uq_cluster_metric_snapshots_cluster_query_task"),
    )
    op.create_index("ix_cluster_metric_snapshots_query_task_id", "cluster_metric_snapshots", ["query_task_id"])
    op.create_index("ix_cluster_metric_snapshots_result_snapshot_id", "cluster_metric_snapshots", ["result_snapshot_id"])
    op.create_index("ix_cluster_metric_snapshots_cluster_window_end", "cluster_metric_snapshots", ["cluster_id", "window_end"])
    op.create_index("ix_cluster_metric_snapshots_discussion_score", "cluster_metric_snapshots", ["discussion_score"])
    op.create_index("ix_cluster_metric_snapshots_growth_score", "cluster_metric_snapshots", ["growth_score"])

    op.create_table(
        "result_snapshot_clusters",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("result_snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cluster_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("board_type", sa.Text(), nullable=False),
        sa.Column("rank_no", sa.Integer(), nullable=False),
        sa.Column("board_score", sa.Numeric(5, 2), nullable=False),
        sa.Column("tie_break_meta", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["result_snapshot_id"], ["result_snapshots.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cluster_id"], ["demand_clusters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("result_snapshot_id", "board_type", "rank_no", name="uq_result_snapshot_clusters_snapshot_board_rank"),
        sa.UniqueConstraint("result_snapshot_id", "board_type", "cluster_id", name="uq_result_snapshot_clusters_snapshot_board_cluster"),
    )
    op.create_index(
        "ix_result_snapshot_clusters_snapshot_board_rank",
        "result_snapshot_clusters",
        ["result_snapshot_id", "board_type", "rank_no"],
    )
    op.create_index("ix_result_snapshot_clusters_cluster_id", "result_snapshot_clusters", ["cluster_id"])

    op.create_table(
        "cluster_evidences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cluster_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("source_ref_id", sa.Text(), nullable=False),
        sa.Column("source_internal_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("excerpt", sa.Text(), nullable=False),
        sa.Column("subreddit_name", sa.Text(), nullable=False),
        sa.Column("source_created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stance", sa.Text(), nullable=False),
        sa.Column("availability_status", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("score_hint", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["cluster_id"], ["demand_clusters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cluster_evidences_cluster_id", "cluster_evidences", ["cluster_id"])
    op.create_index("ix_cluster_evidences_source_type_ref_id", "cluster_evidences", ["source_type", "source_ref_id"])
    op.create_index("ix_cluster_evidences_stance", "cluster_evidences", ["stance"])


def downgrade() -> None:
    op.drop_index("ix_cluster_evidences_stance", table_name="cluster_evidences")
    op.drop_index("ix_cluster_evidences_source_type_ref_id", table_name="cluster_evidences")
    op.drop_index("ix_cluster_evidences_cluster_id", table_name="cluster_evidences")
    op.drop_table("cluster_evidences")

    op.drop_index("ix_result_snapshot_clusters_cluster_id", table_name="result_snapshot_clusters")
    op.drop_index(
        "ix_result_snapshot_clusters_snapshot_board_rank",
        table_name="result_snapshot_clusters",
    )
    op.drop_table("result_snapshot_clusters")

    op.drop_index("ix_cluster_metric_snapshots_growth_score", table_name="cluster_metric_snapshots")
    op.drop_index("ix_cluster_metric_snapshots_discussion_score", table_name="cluster_metric_snapshots")
    op.drop_index(
        "ix_cluster_metric_snapshots_cluster_window_end",
        table_name="cluster_metric_snapshots",
    )
    op.drop_index("ix_cluster_metric_snapshots_result_snapshot_id", table_name="cluster_metric_snapshots")
    op.drop_index("ix_cluster_metric_snapshots_query_task_id", table_name="cluster_metric_snapshots")
    op.drop_table("cluster_metric_snapshots")

    op.drop_index("ix_demand_cluster_aliases_alias_text", table_name="demand_cluster_aliases")
    op.drop_index("ix_demand_cluster_aliases_cluster_id", table_name="demand_cluster_aliases")
    op.drop_table("demand_cluster_aliases")

    op.drop_index("ix_demand_clusters_confidence_score", table_name="demand_clusters")
    op.drop_index("ix_demand_clusters_last_seen_at", table_name="demand_clusters")
    op.drop_index("ix_demand_clusters_cluster_status", table_name="demand_clusters")
    op.drop_table("demand_clusters")
