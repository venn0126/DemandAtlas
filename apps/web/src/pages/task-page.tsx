import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { Badge } from '../components/common/badge'
import { Banner } from '../components/common/banner'
import { Button } from '../components/common/button'
import { Card } from '../components/common/card'
import { ErrorState } from '../components/common/error-state'
import { useI18n } from '../i18n/use-i18n'
import { ProgressBar } from '../components/task/progress-bar'
import { getQueryTaskStatus } from '../services/mock-api'

export function TaskPage() {
  const { t, tDynamic } = useI18n()
  const { queryTaskId } = useParams()
  const [statusMode, setStatusMode] = useState<
    'pending' | 'running' | 'partial_success' | 'success' | 'failed'
  >('running')
  const taskQuery = useQuery({
    queryKey: ['query-task-status', statusMode],
    queryFn: () => getQueryTaskStatus(statusMode),
  })

  const task = taskQuery.data?.data
  const taskError = taskQuery.data?.error
  const canViewResult = Boolean(task?.result_snapshot_id)

  return (
    <section className="page-section">
      <div className="page-header">
        <span className="eyebrow">{t('task.eyebrow')}</span>
        <h1>{t('task.title')}</h1>
        <p className="page-description">{t('task.description')}</p>
      </div>

      <Card className="stack-md">
        <label className="ui-field">
          <span className="ui-field-label">{t('task.scenario.label')}</span>
          <select
            className="ui-input"
            value={statusMode}
            onChange={(event) =>
              setStatusMode(
                event.target.value as 'pending' | 'running' | 'partial_success' | 'success' | 'failed',
              )
            }
          >
            <option value="pending">{tDynamic('enum.taskStatus', 'pending')}</option>
            <option value="running">{tDynamic('enum.taskStatus', 'running')}</option>
            <option value="partial_success">
              {tDynamic('enum.taskStatus', 'partial_success')}
            </option>
            <option value="success">{tDynamic('enum.taskStatus', 'success')}</option>
            <option value="failed">{tDynamic('enum.taskStatus', 'failed')}</option>
          </select>
        </label>
      </Card>

      {taskQuery.isLoading ? (
        <Banner title={t('task.loading.title')} tone="info">
          {t('task.loading.description')}
        </Banner>
      ) : task ? (
        <>
          <Card className="stack-lg">
            <div className="task-status-top">
              <div className="badge-row">
                <Badge
                  tone={
                    task.status === 'failed'
                      ? 'danger'
                      : task.status === 'partial_success'
                        ? 'warning'
                        : task.status === 'success'
                          ? 'success'
                          : 'info'
                  }
                >
                  {tDynamic('enum.taskStatus', task.status)}
                </Badge>
                <Badge>{tDynamic('enum.stage', task.current_stage ?? 'waiting')}</Badge>
              </div>
              <p className="mono-text">{task.query_task_id ?? queryTaskId}</p>
            </div>

            <ProgressBar percent={task.progress.percent} />

            <div className="task-stat-grid">
              <div className="task-stat">
                <span className="task-stat-label">{t('task.stats.currentStep')}</span>
                <strong>{task.progress.current_step}</strong>
              </div>
              <div className="task-stat">
                <span className="task-stat-label">{t('task.stats.totalSteps')}</span>
                <strong>{task.progress.total_steps}</strong>
              </div>
              <div className="task-stat">
                <span className="task-stat-label">{t('task.stats.progress')}</span>
                <strong>{task.progress.percent}%</strong>
              </div>
            </div>
          </Card>

          <Card className="stack-md">
            <h2>{t('task.summary.title')}</h2>
            <p>
              {t('task.summary.queryTaskId')}: {queryTaskId}
            </p>
            <p>
              {t('task.summary.viewType')}: {tDynamic('enum.viewType', 'active')}
            </p>
            <p>
              {t('task.summary.timeWindow')}: {t('common.value.last30Days')}
            </p>
          </Card>

          {task.coverage_note ? (
            <Banner title={t('task.coverage.title')} tone="warning">
              {task.coverage_note}
            </Banner>
          ) : null}

          {task.warnings.length ? (
            <Card className="stack-md">
              <h2>{t('task.warnings.title')}</h2>
              <ul className="bullet-list">
                {task.warnings.map((warning) => (
                  <li key={warning.code}>
                    <strong>{warning.code}</strong>: {warning.message}
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}

          <Card className="stack-md">
            <h2>{t('task.actions.title')}</h2>
            <div className="page-actions">
              <Button onClick={() => void taskQuery.refetch()}>
                {t('task.actions.refresh')}
              </Button>
              <Link to="/discover/directed">
                <Button variant="secondary">{t('task.actions.backToEdit')}</Button>
              </Link>
              {canViewResult ? (
                <Link to={`/results/${task.result_snapshot_id}`}>
                  <Button>{t('task.actions.viewResult')}</Button>
                </Link>
              ) : null}
            </div>
          </Card>

          {task.status === 'failed' && taskError ? (
            <ErrorState
              title={taskError.code}
              description={taskError.message}
              action={
                <Link to="/discover/directed">
                  <Button variant="secondary">{t('task.actions.retryFromQuery')}</Button>
                </Link>
              }
            />
          ) : null}
        </>
      ) : (
        <ErrorState
          title={t('task.error.missingTitle')}
          description={t('task.error.missingDescription')}
        />
      )}
    </section>
  )
}
