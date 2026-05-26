from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, MetaData, Numeric, Text, column, select, table, update
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID

from worker.core.db import engine
from worker.pipeline.types import ClusterRecord, QueryExecutionPlan

metadata = MetaData()

query_tasks_table = table(
    "query_tasks",
    column("id", PGUUID(as_uuid=True)),
    column("status", Text),
    column("query_type", Text),
    column("template_id", PGUUID(as_uuid=True)),
    column("template_version_id", PGUUID(as_uuid=True)),
    column("input_payload", JSONB),
    column("language", Text),
    column("region_hints", JSONB),
    column("min_engagement_threshold", JSONB),
    column("view_type", Text),
    column("window_start", DateTime(timezone=True)),
    column("window_end", DateTime(timezone=True)),
    column("compare_window_start", DateTime(timezone=True)),
    column("compare_window_end", DateTime(timezone=True)),
    column("started_at", DateTime(timezone=True)),
    column("updated_at", DateTime(timezone=True)),
    column("finished_at", DateTime(timezone=True)),
    column("failure_reason", Text),
    column("result_snapshot_id", PGUUID(as_uuid=True)),
)

query_task_run_logs_table = table(
    "query_task_run_logs",
    column("id", PGUUID(as_uuid=True)),
    column("query_task_id", PGUUID(as_uuid=True)),
    column("stage", Text),
    column("status", Text),
    column("message", Text),
    column("meta", JSONB),
    column("started_at", DateTime(timezone=True)),
    column("finished_at", DateTime(timezone=True)),
    column("created_at", DateTime(timezone=True)),
)

result_snapshots_table = table(
    "result_snapshots",
    column("id", PGUUID(as_uuid=True)),
    column("query_task_id", PGUUID(as_uuid=True)),
    column("query_input_snapshot", JSONB),
    column("template_snapshot", JSONB),
    column("summary_stats", JSONB),
    column("coverage_note", Text),
    column("sync_freshness_note", Text),
    column("pipeline_version", Text),
    column("generated_at", DateTime(timezone=True)),
    column("created_at", DateTime(timezone=True)),
    column("updated_at", DateTime(timezone=True)),
)

demand_clusters_table = table(
    "demand_clusters",
    column("id", PGUUID(as_uuid=True)),
    column("canonical_title", Text),
    column("summary", Text),
    column("scenes", JSONB),
    column("pain_points", JSONB),
    column("alternatives", JSONB),
    column("sentiment_profile", JSONB),
    column("confidence_score", Numeric(5, 2)),
    column("cluster_status", Text),
    column("current_version", Integer),
    column("first_seen_at", DateTime(timezone=True)),
    column("last_seen_at", DateTime(timezone=True)),
    column("created_at", DateTime(timezone=True)),
    column("updated_at", DateTime(timezone=True)),
)

demand_cluster_aliases_table = table(
    "demand_cluster_aliases",
    column("id", PGUUID(as_uuid=True)),
    column("cluster_id", PGUUID(as_uuid=True)),
    column("alias_text", Text),
    column("alias_type", Text),
    column("source", Text),
    column("created_at", DateTime(timezone=True)),
)

cluster_metric_snapshots_table = table(
    "cluster_metric_snapshots",
    column("id", PGUUID(as_uuid=True)),
    column("cluster_id", PGUUID(as_uuid=True)),
    column("query_task_id", PGUUID(as_uuid=True)),
    column("result_snapshot_id", PGUUID(as_uuid=True)),
    column("view_type", Text),
    column("window_start", DateTime(timezone=True)),
    column("window_end", DateTime(timezone=True)),
    column("compare_window_start", DateTime(timezone=True)),
    column("compare_window_end", DateTime(timezone=True)),
    column("post_count", Integer),
    column("comment_count", Integer),
    column("unique_user_count", Integer),
    column("avg_comment_depth", Numeric(8, 2)),
    column("avg_post_score", Numeric(10, 2)),
    column("avg_comment_score", Numeric(10, 2)),
    column("high_engagement_post_ratio", Numeric(5, 2)),
    column("community_spread_count", Integer),
    column("discussion_score", Numeric(5, 2)),
    column("attention_score", Numeric(5, 2)),
    column("growth_score", Numeric(5, 2)),
    column("opportunity_score", Numeric(5, 2)),
    column("is_weak_signal", Boolean),
    column("is_low_confidence", Boolean),
    column("is_emerging_signal", Boolean),
    column("created_at", DateTime(timezone=True)),
)

result_snapshot_clusters_table = table(
    "result_snapshot_clusters",
    column("id", PGUUID(as_uuid=True)),
    column("result_snapshot_id", PGUUID(as_uuid=True)),
    column("cluster_id", PGUUID(as_uuid=True)),
    column("board_type", Text),
    column("rank_no", Integer),
    column("board_score", Numeric(5, 2)),
    column("tie_break_meta", JSONB),
    column("created_at", DateTime(timezone=True)),
)

cluster_evidences_table = table(
    "cluster_evidences",
    column("id", PGUUID(as_uuid=True)),
    column("cluster_id", PGUUID(as_uuid=True)),
    column("source_type", Text),
    column("source_ref_id", Text),
    column("source_internal_id", PGUUID(as_uuid=True)),
    column("excerpt", Text),
    column("subreddit_name", Text),
    column("source_created_at", DateTime(timezone=True)),
    column("stance", Text),
    column("availability_status", Text),
    column("source_url", Text),
    column("score_hint", Numeric(10, 2)),
    column("created_at", DateTime(timezone=True)),
)


def utc_now() -> datetime:
    return datetime.now(UTC)


def to_uuid(value: str) -> UUID:
    return UUID(value)


def mark_query_task_running(query_task_id: str) -> None:
    stmt = (
        update(query_tasks_table)
        .where(query_tasks_table.c.id == to_uuid(query_task_id))
        .values(
            status="running",
            started_at=utc_now(),
            updated_at=utc_now(),
        )
    )
    with engine.begin() as connection:
        connection.execute(stmt)


def fetch_query_task_input(query_task_id: str) -> dict:
    stmt = select(query_tasks_table.c.input_payload).where(
        query_tasks_table.c.id == to_uuid(query_task_id)
    )
    with engine.begin() as connection:
        row = connection.execute(stmt).one()
    return row[0] or {}


def fetch_query_task_context(query_task_id: str) -> dict:
    stmt = select(query_tasks_table).where(query_tasks_table.c.id == to_uuid(query_task_id))
    with engine.begin() as connection:
        row = connection.execute(stmt).mappings().one()
    payload = dict(row)
    payload["region_hints"] = payload.get("region_hints") or {}
    payload["min_engagement_threshold"] = payload.get("min_engagement_threshold") or {}
    return payload


def append_stage_log(
    *,
    query_task_id: str,
    stage: str,
    status: str,
    message: str,
    started_at: str,
    finished_at: str,
    current_step: int,
    total_steps: int,
    stage_meta: dict | None = None,
) -> None:
    stmt = query_task_run_logs_table.insert().values(
        id=uuid4(),
        query_task_id=to_uuid(query_task_id),
        stage=stage,
        status=status,
        message=message,
        meta={
            "current_step": current_step,
            "total_steps": total_steps,
            **(stage_meta or {}),
        },
        started_at=datetime.fromisoformat(started_at),
        finished_at=datetime.fromisoformat(finished_at),
        created_at=utc_now(),
    )
    with engine.begin() as connection:
        connection.execute(stmt)


def persist_result_snapshot_bundle(
    *,
    query_task_id: str,
    query_input_snapshot: dict,
    query_plan: QueryExecutionPlan,
    final_status: str,
    summary_stats: dict,
    coverage_note: str | None,
    sync_freshness_note: str | None,
    template_snapshot: dict | None,
    pipeline_version: str,
    clusters: list[ClusterRecord],
    available_boards: list[str],
) -> str:
    result_snapshot_uuid = uuid4()
    now = utc_now()

    with engine.begin() as connection:
        connection.execute(
            result_snapshots_table.insert().values(
                id=result_snapshot_uuid,
                query_task_id=to_uuid(query_task_id),
                query_input_snapshot=query_input_snapshot,
                template_snapshot=template_snapshot,
                summary_stats=summary_stats,
                coverage_note=coverage_note,
                sync_freshness_note=sync_freshness_note,
                pipeline_version=pipeline_version,
                generated_at=now,
                created_at=now,
                updated_at=now,
            )
        )

        cluster_uuid_map: dict[str, UUID] = {}
        for cluster in clusters:
            cluster_uuid = uuid4()
            cluster_uuid_map[cluster.cluster_key] = cluster_uuid
            connection.execute(
                demand_clusters_table.insert().values(
                    id=cluster_uuid,
                    canonical_title=cluster.canonical_title,
                    summary=cluster.summary,
                    scenes=cluster.scenes,
                    pain_points=cluster.pain_points,
                    alternatives=cluster.alternatives,
                    sentiment_profile=cluster.sentiment_profile,
                    confidence_score=cluster.confidence_score,
                    cluster_status="active",
                    current_version=1,
                    first_seen_at=cluster.first_seen_at,
                    last_seen_at=cluster.last_seen_at,
                    created_at=now,
                    updated_at=now,
                )
            )
            alias_rows = [
                {
                    "id": uuid4(),
                    "cluster_id": cluster_uuid,
                    "alias_text": alias_text,
                    "alias_type": "synonym" if alias_text != cluster.canonical_title else "generated_title",
                    "source": "rule",
                    "created_at": now,
                }
                for alias_text in dict.fromkeys(cluster.aliases)
            ]
            if alias_rows:
                connection.execute(demand_cluster_aliases_table.insert(), alias_rows)

            connection.execute(
                cluster_metric_snapshots_table.insert().values(
                    id=uuid4(),
                    cluster_id=cluster_uuid,
                    query_task_id=to_uuid(query_task_id),
                    result_snapshot_id=result_snapshot_uuid,
                    view_type=query_plan.view_type,
                    window_start=query_plan.window_start,
                    window_end=query_plan.window_end,
                    compare_window_start=query_plan.compare_window_start,
                    compare_window_end=query_plan.compare_window_end,
                    post_count=cluster.post_count,
                    comment_count=cluster.comment_count,
                    unique_user_count=cluster.unique_user_count,
                    avg_comment_depth=cluster.avg_comment_depth,
                    avg_post_score=cluster.avg_post_score,
                    avg_comment_score=cluster.avg_comment_score,
                    high_engagement_post_ratio=cluster.high_engagement_post_ratio,
                    community_spread_count=cluster.community_spread_count,
                    discussion_score=cluster.discussion_score,
                    attention_score=cluster.attention_score,
                    growth_score=cluster.growth_score,
                    opportunity_score=cluster.opportunity_score,
                    is_weak_signal=cluster.is_weak_signal,
                    is_low_confidence=cluster.is_low_confidence,
                    is_emerging_signal=cluster.is_emerging_signal,
                    created_at=now,
                )
            )

            evidence_rows = [
                {
                    "id": uuid4(),
                    "cluster_id": cluster_uuid,
                    "source_type": evidence.source_type,
                    "source_ref_id": evidence.source_ref_id,
                    "source_internal_id": None,
                    "excerpt": evidence.excerpt,
                    "subreddit_name": evidence.subreddit_name,
                    "source_created_at": evidence.source_created_at,
                    "stance": evidence.stance,
                    "availability_status": evidence.availability_status,
                    "source_url": evidence.source_url,
                    "score_hint": evidence.score_hint,
                    "created_at": now,
                }
                for evidence in cluster.evidences
            ]
            if evidence_rows:
                connection.execute(cluster_evidences_table.insert(), evidence_rows)

        ranked_clusters = {
            board_type: sorted(
                (
                    cluster
                    for cluster in clusters
                    if board_type != "opportunity" or cluster.opportunity_score is not None
                ),
                key=lambda item: (
                    item.board_scores.get(board_type),
                    item.confidence_score,
                    item.post_count + item.comment_count,
                ),
                reverse=True,
            )
            for board_type in available_boards
        }
        for board_type, board_clusters in ranked_clusters.items():
            for rank_no, cluster in enumerate(board_clusters[:20], start=1):
                connection.execute(
                    result_snapshot_clusters_table.insert().values(
                        id=uuid4(),
                        result_snapshot_id=result_snapshot_uuid,
                        cluster_id=cluster_uuid_map[cluster.cluster_key],
                        board_type=board_type,
                        rank_no=rank_no,
                        board_score=cluster.board_scores[board_type],
                        tie_break_meta=cluster.tie_break_meta,
                        created_at=now,
                    )
                )

        connection.execute(
            update(query_tasks_table)
            .where(query_tasks_table.c.id == to_uuid(query_task_id))
            .values(
                status=final_status,
                result_snapshot_id=result_snapshot_uuid,
                finished_at=now,
                updated_at=now,
            )
        )

    return str(result_snapshot_uuid)


def mark_query_task_failed(query_task_id: str, failure_reason: str) -> None:
    stmt = (
        update(query_tasks_table)
        .where(query_tasks_table.c.id == to_uuid(query_task_id))
        .values(
            status="failed",
            failure_reason=failure_reason,
            finished_at=utc_now(),
            updated_at=utc_now(),
        )
    )
    with engine.begin() as connection:
        connection.execute(stmt)
