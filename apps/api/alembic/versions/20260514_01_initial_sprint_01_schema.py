"""initial sprint 01 schema

Revision ID: 20260514_01
Revises:
Create Date: 2026-05-14 14:40:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260514_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "topic_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("default_language", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_topic_templates_status", "topic_templates", ["status"])

    op.create_table(
        "topic_template_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("keywords", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("synonyms", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("exclude_terms", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("default_view_type", sa.Text(), nullable=False),
        sa.Column("default_sort_strategy", sa.Text(), nullable=False),
        sa.Column("config_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["template_id"], ["topic_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("template_id", "version_no", name="uq_topic_template_versions_template_version"),
    )
    op.create_index(
        "ix_topic_template_versions_template_id",
        "topic_template_versions",
        ["template_id"],
    )

    op.create_table(
        "topic_template_version_subreddits",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subreddit_name", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["template_version_id"], ["topic_template_versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "template_version_id",
            "subreddit_name",
            name="uq_topic_template_version_subreddits_version_subreddit",
        ),
    )
    op.create_index(
        "ix_topic_template_version_subreddits_template_version_id",
        "topic_template_version_subreddits",
        ["template_version_id"],
    )
    op.create_index(
        "ix_topic_template_version_subreddits_subreddit_name",
        "topic_template_version_subreddits",
        ["subreddit_name"],
    )

    op.create_table(
        "query_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("query_type", sa.Text(), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("template_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("input_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("normalized_query_key", sa.Text(), nullable=False),
        sa.Column("language", sa.Text(), nullable=False),
        sa.Column("region_hints", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("min_engagement_threshold", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("view_type", sa.Text(), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("compare_window_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("compare_window_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("pipeline_version", sa.Text(), nullable=False),
        sa.Column("cached_from_snapshot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("result_snapshot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "normalized_query_key",
            "pipeline_version",
            "view_type",
            "window_start",
            "window_end",
            name="uq_query_tasks_dedup_key",
        ),
    )
    op.create_index("ix_query_tasks_status_created_at", "query_tasks", ["status", "created_at"])
    op.create_index("ix_query_tasks_user_id_created_at", "query_tasks", ["user_id", "created_at"])
    op.create_index("ix_query_tasks_result_snapshot_id", "query_tasks", ["result_snapshot_id"])

    op.create_table(
        "query_task_run_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stage", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_query_task_run_logs_query_task_id_created_at",
        "query_task_run_logs",
        ["query_task_id", "created_at"],
    )
    op.create_index(
        "ix_query_task_run_logs_stage_status",
        "query_task_run_logs",
        ["stage", "status"],
    )

    op.create_table(
        "result_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("query_input_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("template_snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("summary_stats", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("coverage_note", sa.Text(), nullable=True),
        sa.Column("sync_freshness_note", sa.Text(), nullable=True),
        sa.Column("pipeline_version", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("query_task_id", name="uq_result_snapshots_query_task_id"),
    )
    op.create_index("ix_result_snapshots_generated_at", "result_snapshots", ["generated_at"])


def downgrade() -> None:
    op.drop_index("ix_result_snapshots_generated_at", table_name="result_snapshots")
    op.drop_table("result_snapshots")

    op.drop_index("ix_query_task_run_logs_stage_status", table_name="query_task_run_logs")
    op.drop_index(
        "ix_query_task_run_logs_query_task_id_created_at",
        table_name="query_task_run_logs",
    )
    op.drop_table("query_task_run_logs")

    op.drop_index("ix_query_tasks_result_snapshot_id", table_name="query_tasks")
    op.drop_index("ix_query_tasks_user_id_created_at", table_name="query_tasks")
    op.drop_index("ix_query_tasks_status_created_at", table_name="query_tasks")
    op.drop_table("query_tasks")

    op.drop_index(
        "ix_topic_template_version_subreddits_subreddit_name",
        table_name="topic_template_version_subreddits",
    )
    op.drop_index(
        "ix_topic_template_version_subreddits_template_version_id",
        table_name="topic_template_version_subreddits",
    )
    op.drop_table("topic_template_version_subreddits")

    op.drop_index("ix_topic_template_versions_template_id", table_name="topic_template_versions")
    op.drop_table("topic_template_versions")

    op.drop_index("ix_topic_templates_status", table_name="topic_templates")
    op.drop_table("topic_templates")
