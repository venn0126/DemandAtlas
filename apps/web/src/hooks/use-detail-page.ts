import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import {
  toDetailMetricViewModels,
  toDetailOverviewRows,
  toDetailScoreViewModels,
} from '../adapters/detail'
import { useI18n } from '../i18n/use-i18n'
import { formatUtcDateTime } from '../lib/format'
import { getClusterDetail } from '../services/mock-api'

export function useDetailPage() {
  const { locale, t } = useI18n()
  const { resultSnapshotId, clusterId } = useParams()
  const detailMode =
    clusterId === 'clu_01JVA2HFQYEXN30A94M4EN2HNB' ? 'partial' : 'normal'

  const detailQuery = useQuery({
    queryKey: ['cluster-detail', clusterId, detailMode],
    queryFn: () => getClusterDetail(detailMode),
  })

  const detail = detailQuery.data?.data
  const overviewRows = detail
    ? toDetailOverviewRows({
        resultSnapshotLabel: t('detail.meta.resultSnapshotId'),
        resultSnapshotValue: resultSnapshotId ?? '',
        timeWindowLabel: t('detail.meta.timeWindow'),
        timeWindowValue: `${formatUtcDateTime(detail.time_window.start_at, locale)} - ${formatUtcDateTime(detail.time_window.end_at, locale)}`,
      })
    : []
  const scoreRows = detail
    ? toDetailScoreViewModels(detail, {
        discussion: t('detail.scores.discussion'),
        attention: t('detail.scores.attention'),
        growth: t('detail.scores.growth'),
        opportunity: t('detail.scores.opportunity'),
        confidence: t('detail.scores.confidence'),
      })
    : []
  const metricRows = detail
    ? toDetailMetricViewModels(detail, {
        posts: t('detail.metrics.posts'),
        comments: t('detail.metrics.comments'),
        users: t('detail.metrics.users'),
        communities: t('detail.metrics.communities'),
      })
    : []

  return {
    title: t('detail.title'),
    eyebrow: t('detail.eyebrow'),
    description: t('detail.description'),
    resultSnapshotId,
    detailQuery,
    detail,
    overviewRows,
    scoreRows,
    metricRows,
    labels: {
      loadingTitle: t('detail.loading.title'),
      errorTitle: t('detail.error.title'),
      errorDescription: t('detail.error.description'),
      coverageTitle: t('detail.coverage.title'),
      overview: {
        resultSnapshotLabel: overviewRows[0]?.label ?? '',
        timeWindowLabel: overviewRows[1]?.label ?? '',
        timeWindowValue: overviewRows[1]?.value ?? '',
        emergingLabel: t('detail.badge.emerging'),
        lowConfidenceLabel: t('detail.badge.lowConfidence'),
        weakSignalLabel: t('detail.badge.weakSignal'),
      },
      metrics: {
        title: t('detail.metrics.title'),
        posts: metricRows[0]?.label ?? '',
        comments: metricRows[1]?.label ?? '',
        users: metricRows[2]?.label ?? '',
        communities: metricRows[3]?.label ?? '',
      },
      context: {
        title: t('detail.context.title'),
        scenes: t('detail.context.scenes'),
        painPoints: t('detail.context.painPoints'),
        alternatives: t('detail.context.alternatives'),
      },
      evidence: {
        supporting: t('detail.supportingEvidence.title'),
        opposing: t('detail.opposingEvidence.title'),
      },
    },
  }
}
