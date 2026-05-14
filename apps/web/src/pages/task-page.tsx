import { Link } from 'react-router-dom'

import { routeBuilders, routes } from '../app/routes'
import { Banner } from '../components/common/banner'
import { Button } from '../components/common/button'
import { Card } from '../components/common/card'
import { ErrorState } from '../components/common/error-state'
import { SelectField } from '../components/common/select-field'
import { InlineGroup } from '../components/layout/inline-group'
import { Page } from '../components/layout/page'
import { PageHeader } from '../components/layout/page-header'
import { Stack } from '../components/layout/stack'
import { useTaskPage } from '../hooks/use-task-page'
import { TaskStatusCard } from '../components/task/task-status-card'
import { TaskSummaryCard } from '../components/task/task-summary-card'

export function TaskPage() {
  const vm = useTaskPage()

  return (
    <Page>
      <PageHeader
        eyebrow={vm.eyebrow}
        title={vm.title}
        description={vm.description}
      />

      <Card>
        <Stack gap="md">
          <SelectField
            label={vm.labels.scenario}
            value={vm.statusMode}
            onChange={(event) =>
              vm.setStatusMode(
                event.target.value as 'pending' | 'running' | 'partial_success' | 'success' | 'failed',
              )
            }
            options={vm.statusOptions}
          />
        </Stack>
      </Card>

      {vm.taskQuery.isLoading ? (
        <Banner title={vm.labels.loadingTitle} tone="info">
          {vm.labels.loadingDescription}
        </Banner>
      ) : vm.task ? (
        <>
          <Card className="stack-lg">
            <TaskStatusCard
              taskId={vm.taskStatusViewModel?.taskId ?? ''}
              statusLabel={vm.taskStatusViewModel?.statusLabel ?? ''}
              stageLabel={vm.taskStatusViewModel?.stageLabel ?? ''}
              statusTone={vm.taskStatusViewModel?.statusTone ?? 'info'}
              currentStep={vm.taskStatusViewModel?.currentStep ?? 0}
              totalSteps={vm.taskStatusViewModel?.totalSteps ?? 0}
              progressPercent={vm.taskStatusViewModel?.progressPercent ?? 0}
              currentStepLabel={vm.labels.currentStep}
              totalStepsLabel={vm.labels.totalSteps}
              progressLabel={vm.labels.progress}
            />
          </Card>

          <Card>
            <TaskSummaryCard title={vm.labels.summaryTitle} rows={vm.summaryRows} />
          </Card>

          {vm.task.coverage_note ? (
            <Banner title={vm.labels.coverageTitle} tone="warning">
              {vm.task.coverage_note}
            </Banner>
          ) : null}

          {vm.task.warnings.length ? (
            <Card>
              <Stack gap="md">
                <h2>{vm.labels.warningsTitle}</h2>
                <ul className="bullet-list">
                  {vm.task.warnings.map((warning) => (
                    <li key={warning.code}>
                      <strong>{warning.code}</strong>: {warning.message}
                    </li>
                  ))}
                </ul>
              </Stack>
            </Card>
          ) : null}

          <Card>
            <Stack gap="md">
              <h2>{vm.labels.actionsTitle}</h2>
              <InlineGroup variant="actions">
                <Button onClick={() => void vm.taskQuery.refetch()}>
                  {vm.labels.refresh}
                </Button>
                <Link to={routes.directed}>
                  <Button variant="secondary">{vm.labels.backToEdit}</Button>
                </Link>
                {vm.canViewResult && vm.task.result_snapshot_id ? (
                  <Link to={routeBuilders.result(vm.task.result_snapshot_id)}>
                    <Button>{vm.labels.viewResult}</Button>
                  </Link>
                ) : null}
              </InlineGroup>
            </Stack>
          </Card>

          {vm.task.status === 'failed' && vm.taskError ? (
            <ErrorState
              title={vm.taskError.code}
              description={vm.taskError.message}
              action={
                <Link to={routes.directed}>
                  <Button variant="secondary">{vm.labels.retryFromQuery}</Button>
                </Link>
              }
            />
          ) : null}
        </>
      ) : (
        <ErrorState
          title={vm.labels.missingTitle}
          description={vm.labels.missingDescription}
        />
      )}
    </Page>
  )
}
