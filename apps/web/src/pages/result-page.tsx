import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { Badge } from '../components/common/badge'
import { Banner } from '../components/common/banner'
import { Card } from '../components/common/card'
import { EmptyState } from '../components/common/empty-state'
import { ErrorState } from '../components/common/error-state'
import { LoadingState } from '../components/common/loading-state'
import { Tabs } from '../components/common/tabs'
import { useI18n } from '../i18n/use-i18n'
import { formatUtcDateTime } from '../lib/format'
import { queryKeys } from '../lib/query-keys'
import { getBoardResult, getResultSnapshotSummary } from '../services/mock-api'

export function ResultPage() {
  const { locale, t, tDynamic } = useI18n()
  const navigate = useNavigate()
  const { resultSnapshotId, boardType } = useParams()
  const [activeBoard, setActiveBoard] = useState(boardType ?? 'hot')

  const summaryMode =
    resultSnapshotId === 'rs_01JVA1PAB2Y9PGKQ7NH1AK6R9M'
      ? 'partial'
      : resultSnapshotId === 'rs_01JVA2120R3D39SY1CMN18R8QW'
        ? 'empty'
        : 'normal'

  const summaryQuery = useQuery({
    queryKey: [...queryKeys.resultPreview, resultSnapshotId, summaryMode],
    queryFn: () => getResultSnapshotSummary(summaryMode),
  })

  const boardQuery = useQuery({
    queryKey: ['board-result', resultSnapshotId, activeBoard, summaryMode],
    queryFn: () =>
      getBoardResult(summaryMode === 'empty' ? 'empty' : (activeBoard as 'hot' | 'growth' | 'opportunity')),
  })

  const summary = summaryQuery.data?.data
  const board = boardQuery.data?.data

  return (
    <section className="page-section">
      <div className="page-header">
        <span className="eyebrow">{t('result.eyebrow')}</span>
        <h1>{t('result.title')}</h1>
        <p className="page-description">{t('result.description')}</p>
      </div>

      {summaryQuery.isLoading ? (
        <LoadingState title={t('result.loadingSummary.title')} />
      ) : null}
      {summaryQuery.isError ? (
        <ErrorState
          title={t('result.errorSummary.title')}
          description={t('result.errorSummary.description')}
        />
      ) : null}

      {summary ? (
        <>
          <Card className="stack-lg">
            <div className="task-status-top">
              <div className="badge-row">
                <Badge tone="success">{tDynamic('enum.viewType', summary.view_type)}</Badge>
                <Badge>{tDynamic('enum.queryType', summary.query_type)}</Badge>
              </div>
              <p className="mono-text">{summary.result_snapshot_id}</p>
            </div>

            <div className="task-stat-grid">
              <div className="task-stat">
                <span className="task-stat-label">{t('result.stats.clusters')}</span>
                <strong>{summary.summary_stats.cluster_count}</strong>
              </div>
              <div className="task-stat">
                <span className="task-stat-label">{t('result.stats.posts')}</span>
                <strong>{summary.summary_stats.post_count}</strong>
              </div>
              <div className="task-stat">
                <span className="task-stat-label">{t('result.stats.comments')}</span>
                <strong>{summary.summary_stats.comment_count}</strong>
              </div>
            </div>

            <div className="stack-md">
              <p>
                {t('result.meta.queryTaskId')}: {summary.query_task_id}
              </p>
              <p>
                {t('result.meta.generatedAt')}:{' '}
                {formatUtcDateTime(summary.generated_at, locale)}
              </p>
            </div>
          </Card>

          {summary.coverage_note ? (
            <Banner title={t('result.coverage.title')} tone="warning">
              {summary.coverage_note}
            </Banner>
          ) : null}

          <Banner title={t('result.freshness.title')} tone="info">
            {summary.sync_freshness_note}
          </Banner>

          <Card className="stack-lg">
            <div className="task-status-top">
              <Tabs
                value={activeBoard}
                onChange={(value) => {
                  setActiveBoard(value)
                  navigate(`/results/${resultSnapshotId}/boards/${value}`)
                }}
                items={summary.available_boards.map((item) => ({
                  key: item,
                  label: tDynamic('enum.boardType', item),
                }))}
              />
            </div>

            {boardQuery.isLoading ? (
              <LoadingState title={t('result.loadingBoard.title')} />
            ) : null}
            {boardQuery.isError ? (
              <ErrorState
                title={t('result.errorBoard.title')}
                description={t('result.errorBoard.description')}
              />
            ) : null}

            {board?.items.length ? (
              <div className="result-list">
                {board.items.map((item) => (
                  <Link
                    key={item.cluster_id}
                    to={`/results/${resultSnapshotId}/clusters/${item.cluster_id}`}
                    className="result-link"
                  >
                    <article className="result-item">
                      <div className="task-status-top">
                        <div>
                          <p className="mono-text">#{item.rank}</p>
                          <h3>{item.title}</h3>
                        </div>
                        <div className="badge-row">
                          <Badge tone="info">{item.board_score.toFixed(1)}</Badge>
                          {item.is_emerging_signal ? (
                            <Badge tone="info">{t('result.badge.emerging')}</Badge>
                          ) : null}
                          {item.is_low_confidence ? (
                            <Badge tone="warning">{t('result.badge.lowConfidence')}</Badge>
                          ) : null}
                          {item.is_weak_signal ? (
                            <Badge tone="warning">{t('result.badge.weakSignal')}</Badge>
                          ) : null}
                        </div>
                      </div>

                      <p>{item.summary}</p>

                      <div className="badge-row">
                        {item.top_subreddits.map((subreddit) => (
                          <Badge key={subreddit}>{subreddit}</Badge>
                        ))}
                      </div>
                    </article>
                  </Link>
                ))}
              </div>
            ) : (
              <EmptyState
                title={t('result.empty.title')}
                description={t('result.empty.description')}
              />
            )}
          </Card>
        </>
      ) : null}
    </section>
  )
}
