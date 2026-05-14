import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'

import { toTaskStatusViewModel, toTaskSummaryRows } from '../adapters/query'
import { useI18n } from '../i18n/use-i18n'
import { getQueryTaskStatus } from '../services/mock-api'
import type { QueryTaskStatus } from '../types/query'

export function useTaskPage() {
  const { t, tDynamic } = useI18n()
  const { queryTaskId } = useParams()
  const [statusMode, setStatusMode] = useState<QueryTaskStatus>('running')

  const taskQuery = useQuery({
    queryKey: ['query-task-status', statusMode],
    queryFn: () => getQueryTaskStatus(statusMode),
  })

  const task = taskQuery.data?.data
  const taskError = taskQuery.data?.error
  const canViewResult = Boolean(task?.result_snapshot_id)

  const taskStatusViewModel = task
    ? toTaskStatusViewModel({
        task,
        taskIdFallback: queryTaskId ?? '',
        statusLabel: tDynamic('enum.taskStatus', task.status),
        stageLabel: tDynamic('enum.stage', task.current_stage ?? 'waiting'),
      })
    : null

  const summaryRows = toTaskSummaryRows([
    {
      label: t('task.summary.queryTaskId'),
      value: queryTaskId ?? '',
    },
    {
      label: t('task.summary.viewType'),
      value: tDynamic('enum.viewType', 'active'),
    },
    {
      label: t('task.summary.timeWindow'),
      value: t('common.value.last30Days'),
    },
  ])

  return {
    title: t('task.title'),
    eyebrow: t('task.eyebrow'),
    description: t('task.description'),
    taskQuery,
    task,
    taskError,
    queryTaskId,
    statusMode,
    setStatusMode,
    taskStatusViewModel,
    summaryRows,
    canViewResult,
    labels: {
      scenario: t('task.scenario.label'),
      loadingTitle: t('task.loading.title'),
      loadingDescription: t('task.loading.description'),
      currentStep: t('task.stats.currentStep'),
      totalSteps: t('task.stats.totalSteps'),
      progress: t('task.stats.progress'),
      summaryTitle: t('task.summary.title'),
      coverageTitle: t('task.coverage.title'),
      warningsTitle: t('task.warnings.title'),
      actionsTitle: t('task.actions.title'),
      refresh: t('task.actions.refresh'),
      backToEdit: t('task.actions.backToEdit'),
      viewResult: t('task.actions.viewResult'),
      retryFromQuery: t('task.actions.retryFromQuery'),
      missingTitle: t('task.error.missingTitle'),
      missingDescription: t('task.error.missingDescription'),
    },
    statusOptions: [
      { value: 'pending', label: tDynamic('enum.taskStatus', 'pending') },
      { value: 'running', label: tDynamic('enum.taskStatus', 'running') },
      { value: 'partial_success', label: tDynamic('enum.taskStatus', 'partial_success') },
      { value: 'success', label: tDynamic('enum.taskStatus', 'success') },
      { value: 'failed', label: tDynamic('enum.taskStatus', 'failed') },
    ],
  }
}
