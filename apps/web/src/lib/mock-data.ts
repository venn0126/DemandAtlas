import clusterDetailNormal from '../../../../frontend/mock/cluster-detail.normal.json'
import clusterDetailPartialEvidence from '../../../../frontend/mock/cluster-detail.partial-evidence.json'
import queryTaskCreateAsync from '../../../../frontend/mock/query-task.create.async.json'
import queryTaskCreateCacheHit from '../../../../frontend/mock/query-task.create.cache-hit.json'
import queryTaskStatusFailed from '../../../../frontend/mock/query-task.status.failed.json'
import queryTaskStatusPartialSuccess from '../../../../frontend/mock/query-task.status.partial-success.json'
import queryTaskStatusPending from '../../../../frontend/mock/query-task.status.pending.json'
import queryTaskStatusRunning from '../../../../frontend/mock/query-task.status.running.json'
import queryTaskStatusSuccess from '../../../../frontend/mock/query-task.status.success.json'
import resultSnapshotBoardEmpty from '../../../../frontend/mock/result-snapshot.board.empty.json'
import resultSnapshotBoardGrowth from '../../../../frontend/mock/result-snapshot.board.growth.json'
import resultSnapshotBoardHot from '../../../../frontend/mock/result-snapshot.board.hot.json'
import resultSnapshotBoardOpportunity from '../../../../frontend/mock/result-snapshot.board.opportunity.json'
import resultSnapshotSummaryEmpty from '../../../../frontend/mock/result-snapshot.summary.empty.json'
import resultSnapshotSummaryNormal from '../../../../frontend/mock/result-snapshot.summary.normal.json'
import resultSnapshotSummaryPartial from '../../../../frontend/mock/result-snapshot.summary.partial.json'
import topicTemplateDetail from '../../../../frontend/mock/topic-template.detail.json'
import topicTemplatesList from '../../../../frontend/mock/topic-templates.list.json'

export const mockData = {
  topicTemplatesList,
  topicTemplateDetail,
  queryTaskCreateAsync,
  queryTaskCreateCacheHit,
  queryTaskStatusPending,
  queryTaskStatusRunning,
  queryTaskStatusPartialSuccess,
  queryTaskStatusSuccess,
  queryTaskStatusFailed,
  resultSnapshotSummaryNormal,
  resultSnapshotSummaryEmpty,
  resultSnapshotSummaryPartial,
  resultSnapshotBoardHot,
  resultSnapshotBoardGrowth,
  resultSnapshotBoardOpportunity,
  resultSnapshotBoardEmpty,
  clusterDetailNormal,
  clusterDetailPartialEvidence,
} as const
