import type { BoardItem, ResultSnapshotSummary } from '../types/result'
import type {
  KeyValueRowViewModel,
  MetricViewModel,
  ResultBoardItemViewModel,
  SelectOptionViewModel,
} from '../types/view-model'

export function toResultMetrics(summary: ResultSnapshotSummary, labels: {
  clusters: string
  posts: string
  comments: string
}): MetricViewModel[] {
  return [
    { label: labels.clusters, value: summary.summary_stats.cluster_count },
    { label: labels.posts, value: summary.summary_stats.post_count },
    { label: labels.comments, value: summary.summary_stats.comment_count },
  ]
}

export function toResultMetaRows(input: {
  summary: ResultSnapshotSummary
  queryTaskIdLabel: string
  generatedAtLabel: string
  generatedAtValue: string
}): KeyValueRowViewModel[] {
  return [
    {
      label: input.queryTaskIdLabel,
      value: input.summary.query_task_id,
    },
    {
      label: input.generatedAtLabel,
      value: input.generatedAtValue,
    },
  ]
}

export function toBoardTabOptions(
  availableBoards: ResultSnapshotSummary['available_boards'],
  labelFor: (value: string) => string,
): SelectOptionViewModel[] {
  return availableBoards.map((item) => ({
    value: item,
    label: labelFor(item),
  }))
}

export function toResultBoardItemViewModel(item: BoardItem): ResultBoardItemViewModel {
  return {
    clusterId: item.cluster_id,
    rank: item.rank,
    title: item.title,
    summary: item.summary,
    boardScore: item.board_score,
    topSubreddits: item.top_subreddits,
    isEmergingSignal: item.is_emerging_signal,
    isLowConfidence: item.is_low_confidence,
    isWeakSignal: item.is_weak_signal,
  }
}
