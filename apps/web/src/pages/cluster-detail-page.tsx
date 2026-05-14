import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import { Badge } from '../components/common/badge'
import { Banner } from '../components/common/banner'
import { Card } from '../components/common/card'
import { ErrorState } from '../components/common/error-state'
import { LoadingState } from '../components/common/loading-state'
import { useI18n } from '../i18n/use-i18n'
import { formatUtcDateTime } from '../lib/format'
import { EvidenceCard } from '../components/result/evidence-card'
import { ScorePill } from '../components/result/score-pill'
import { getClusterDetail } from '../services/mock-api'

export function ClusterDetailPage() {
  const { locale, t } = useI18n()
  const { resultSnapshotId, clusterId } = useParams()
  const detailMode =
    clusterId === 'clu_01JVA2HFQYEXN30A94M4EN2HNB' ? 'partial' : 'normal'

  const detailQuery = useQuery({
    queryKey: ['cluster-detail', clusterId, detailMode],
    queryFn: () => getClusterDetail(detailMode),
  })

  const detail = detailQuery.data?.data

  return (
    <section className="page-section">
      <div className="page-header">
        <span className="eyebrow">{t('detail.eyebrow')}</span>
        <h1>{t('detail.title')}</h1>
        <p className="page-description">{t('detail.description')}</p>
      </div>

      {detailQuery.isLoading ? <LoadingState title={t('detail.loading.title')} /> : null}
      {detailQuery.isError ? (
        <ErrorState
          title={t('detail.error.title')}
          description={t('detail.error.description')}
        />
      ) : null}

      {detail ? (
        <>
          <Card className="stack-lg">
            <div className="task-status-top">
              <div className="badge-row">
                {detail.flags.is_emerging_signal ? (
                  <Badge tone="info">{t('detail.badge.emerging')}</Badge>
                ) : null}
                {detail.flags.is_low_confidence ? (
                  <Badge tone="warning">{t('detail.badge.lowConfidence')}</Badge>
                ) : null}
                {detail.flags.is_weak_signal ? (
                  <Badge tone="warning">{t('detail.badge.weakSignal')}</Badge>
                ) : null}
              </div>
              <p className="mono-text">{resultSnapshotId}</p>
            </div>

            <div>
              <h2>{detail.title}</h2>
              <p>{detail.summary}</p>
              <p>
                {t('detail.meta.resultSnapshotId')}: {resultSnapshotId}
              </p>
              <p>
                {t('detail.meta.timeWindow')}:{' '}
                {formatUtcDateTime(detail.time_window.start_at, locale)} -{' '}
                {formatUtcDateTime(detail.time_window.end_at, locale)}
              </p>
            </div>

            <div className="score-grid">
              <ScorePill label={t('detail.scores.discussion')} value={detail.scores.discussion_score} />
              <ScorePill label={t('detail.scores.attention')} value={detail.scores.attention_score} />
              <ScorePill label={t('detail.scores.growth')} value={detail.scores.growth_score} />
              <ScorePill
                label={t('detail.scores.opportunity')}
                value={detail.scores.opportunity_score}
              />
              <ScorePill label={t('detail.scores.confidence')} value={detail.scores.confidence_score} />
            </div>
          </Card>

          {detail.coverage_note ? (
            <Banner title={t('detail.coverage.title')} tone="warning">
              {detail.coverage_note}
            </Banner>
          ) : null}

          <Card className="stack-lg">
            <h2>{t('detail.metrics.title')}</h2>
            <div className="task-stat-grid">
              <div className="task-stat">
                <span className="task-stat-label">{t('detail.metrics.posts')}</span>
                <strong>{detail.metrics.post_count}</strong>
              </div>
              <div className="task-stat">
                <span className="task-stat-label">{t('detail.metrics.comments')}</span>
                <strong>{detail.metrics.comment_count}</strong>
              </div>
              <div className="task-stat">
                <span className="task-stat-label">{t('detail.metrics.users')}</span>
                <strong>{detail.metrics.unique_user_count}</strong>
              </div>
              <div className="task-stat">
                <span className="task-stat-label">{t('detail.metrics.communities')}</span>
                <strong>{detail.metrics.community_spread_count}</strong>
              </div>
            </div>
          </Card>

          <Card className="stack-lg">
            <h2>{t('detail.context.title')}</h2>
            <div className="stack-md">
              <div>
                <p className="section-label">{t('detail.context.scenes')}</p>
                <div className="badge-row">
                  {detail.scenes.map((scene) => (
                    <Badge key={scene}>{scene}</Badge>
                  ))}
                </div>
              </div>
              <div>
                <p className="section-label">{t('detail.context.painPoints')}</p>
                <div className="badge-row">
                  {detail.pain_points.map((item) => (
                    <Badge key={item} tone="warning">
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
              <div>
                <p className="section-label">{t('detail.context.alternatives')}</p>
                <div className="badge-row">
                  {detail.alternatives.map((item) => (
                    <Badge key={item} tone="info">
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </Card>

          <Card className="stack-lg">
            <h2>{t('detail.supportingEvidence.title')}</h2>
            <div className="stack-md">
              {detail.supporting_evidence.map((item) => (
                <EvidenceCard
                  key={item.evidence_id}
                  excerpt={item.excerpt}
                  subreddit={item.subreddit}
                  createdAt={item.created_at}
                  availabilityStatus={item.availability_status}
                  sourceUrl={item.source_url}
                />
              ))}
            </div>
          </Card>

          {detail.opposing_evidence.length ? (
            <Card className="stack-lg">
              <h2>{t('detail.opposingEvidence.title')}</h2>
              <div className="stack-md">
                {detail.opposing_evidence.map((item) => (
                  <EvidenceCard
                    key={item.evidence_id}
                    excerpt={item.excerpt}
                    subreddit={item.subreddit}
                    createdAt={item.created_at}
                    availabilityStatus={item.availability_status}
                    sourceUrl={item.source_url}
                  />
                ))}
              </div>
            </Card>
          ) : null}
        </>
      ) : null}
    </section>
  )
}
