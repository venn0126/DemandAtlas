import type { ClusterDetail } from '../types/detail'
import type { KeyValueRowViewModel, MetricViewModel, ScoreViewModel } from '../types/view-model'

export function toDetailOverviewRows(input: {
  resultSnapshotLabel: string
  resultSnapshotValue: string
  timeWindowLabel: string
  timeWindowValue: string
}): KeyValueRowViewModel[] {
  return [
    {
      label: input.resultSnapshotLabel,
      value: input.resultSnapshotValue,
    },
    {
      label: input.timeWindowLabel,
      value: input.timeWindowValue,
    },
  ]
}

export function toDetailScoreViewModels(
  detail: ClusterDetail,
  labels: {
    discussion: string
    attention: string
    growth: string
    opportunity: string
    confidence: string
  },
): ScoreViewModel[] {
  return [
    { label: labels.discussion, value: detail.scores.discussion_score },
    { label: labels.attention, value: detail.scores.attention_score },
    { label: labels.growth, value: detail.scores.growth_score },
    { label: labels.opportunity, value: detail.scores.opportunity_score },
    { label: labels.confidence, value: detail.scores.confidence_score },
  ]
}

export function toDetailMetricViewModels(
  detail: ClusterDetail,
  labels: {
    posts: string
    comments: string
    users: string
    communities: string
  },
): MetricViewModel[] {
  return [
    { label: labels.posts, value: detail.metrics.post_count },
    { label: labels.comments, value: detail.metrics.comment_count },
    { label: labels.users, value: detail.metrics.unique_user_count },
    { label: labels.communities, value: detail.metrics.community_spread_count },
  ]
}
