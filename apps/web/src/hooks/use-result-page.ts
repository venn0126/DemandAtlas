import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import {
  toBoardTabOptions,
  toResultBoardItemViewModel,
  toResultMetaRows,
  toResultMetrics,
} from '../adapters/result'
import { useI18n } from '../i18n/use-i18n'
import { formatUtcDateTime } from '../lib/format'
import { queryKeys } from '../lib/query-keys'
import { getBoardResult, getResultSnapshotSummary } from '../services/mock-api'

export function useResultPage() {
  const { locale, t, tDynamic } = useI18n()
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
  const resultMetrics = summary
    ? toResultMetrics(summary, {
        clusters: t('result.stats.clusters'),
        posts: t('result.stats.posts'),
        comments: t('result.stats.comments'),
      })
    : []
  const resultMetaRows = summary
    ? toResultMetaRows({
        summary,
        queryTaskIdLabel: t('result.meta.queryTaskId'),
        generatedAtLabel: t('result.meta.generatedAt'),
        generatedAtValue: formatUtcDateTime(summary.generated_at, locale),
      })
    : []
  const boardTabOptions = summary
    ? toBoardTabOptions(summary.available_boards, (value) => tDynamic('enum.boardType', value))
    : []
  const boardItems = board?.items.map((item) => toResultBoardItemViewModel(item)) ?? []

  return {
    title: t('result.title'),
    eyebrow: t('result.eyebrow'),
    description: t('result.description'),
    resultSnapshotId,
    activeBoard,
    setActiveBoard,
    summaryQuery,
    boardQuery,
    summary,
    board,
    resultMetrics,
    resultMetaRows,
    boardTabOptions,
    boardItems,
    labels: {
      loadingSummary: t('result.loadingSummary.title'),
      errorSummaryTitle: t('result.errorSummary.title'),
      errorSummaryDescription: t('result.errorSummary.description'),
      loadingBoard: t('result.loadingBoard.title'),
      errorBoardTitle: t('result.errorBoard.title'),
      errorBoardDescription: t('result.errorBoard.description'),
      coverageTitle: t('result.coverage.title'),
      freshnessTitle: t('result.freshness.title'),
      clusterLabel: resultMetrics[0]?.label ?? '',
      postLabel: resultMetrics[1]?.label ?? '',
      commentLabel: resultMetrics[2]?.label ?? '',
      queryTaskIdLabel: resultMetaRows[0]?.label ?? '',
      generatedAtLabel: resultMetaRows[1]?.label ?? '',
      generatedAtValue: resultMetaRows[1]?.value ?? '',
      emerging: t('result.badge.emerging'),
      lowConfidence: t('result.badge.lowConfidence'),
      weakSignal: t('result.badge.weakSignal'),
      emptyTitle: t('result.empty.title'),
      emptyDescription: t('result.empty.description'),
    },
  }
}
