from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.demand_cluster import (
    ClusterEvidence,
    ClusterMetricSnapshot,
    DemandCluster,
    ResultSnapshotCluster,
)
from app.models.result_snapshot import ResultSnapshot


def get_result_snapshot_by_id(db: Session, result_snapshot_id: UUID) -> ResultSnapshot | None:
    stmt = (
        select(ResultSnapshot)
        .options(
            selectinload(ResultSnapshot.query_task),
            selectinload(ResultSnapshot.metric_snapshots).selectinload(ClusterMetricSnapshot.cluster),
            selectinload(ResultSnapshot.snapshot_clusters).selectinload(ResultSnapshotCluster.cluster),
        )
        .where(ResultSnapshot.id == result_snapshot_id)
    )
    return db.scalar(stmt)


def list_snapshot_board_entries(
    db: Session,
    *,
    result_snapshot_id: UUID,
    board_type: str,
) -> list[tuple[ResultSnapshotCluster, DemandCluster, ClusterMetricSnapshot | None]]:
    stmt = (
        select(ResultSnapshotCluster, DemandCluster, ClusterMetricSnapshot)
        .join(DemandCluster, DemandCluster.id == ResultSnapshotCluster.cluster_id)
        .outerjoin(
            ClusterMetricSnapshot,
            (ClusterMetricSnapshot.cluster_id == ResultSnapshotCluster.cluster_id)
            & (ClusterMetricSnapshot.result_snapshot_id == ResultSnapshotCluster.result_snapshot_id),
        )
        .where(ResultSnapshotCluster.result_snapshot_id == result_snapshot_id)
        .where(ResultSnapshotCluster.board_type == board_type)
        .order_by(ResultSnapshotCluster.rank_no.asc())
    )
    return list(db.execute(stmt).all())


def get_cluster_detail_bundle(
    db: Session,
    *,
    result_snapshot_id: UUID,
    cluster_id: UUID,
) -> tuple[DemandCluster, ClusterMetricSnapshot | None, list[ClusterEvidence], list[ResultSnapshotCluster]] | None:
    cluster_stmt = select(DemandCluster).where(DemandCluster.id == cluster_id)
    cluster = db.scalar(cluster_stmt)
    if cluster is None:
        return None

    metric_stmt = select(ClusterMetricSnapshot).where(
        ClusterMetricSnapshot.result_snapshot_id == result_snapshot_id,
        ClusterMetricSnapshot.cluster_id == cluster_id,
    )
    evidence_stmt = (
        select(ClusterEvidence)
        .where(ClusterEvidence.cluster_id == cluster_id)
        .order_by(ClusterEvidence.score_hint.desc().nullslast(), ClusterEvidence.created_at.asc())
    )
    board_stmt = select(ResultSnapshotCluster).where(
        ResultSnapshotCluster.result_snapshot_id == result_snapshot_id,
        ResultSnapshotCluster.cluster_id == cluster_id,
    )

    metric = db.scalar(metric_stmt)
    evidences = list(db.scalars(evidence_stmt).all())
    board_entries = list(db.scalars(board_stmt).all())
    return cluster, metric, evidences, board_entries
