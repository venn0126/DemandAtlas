import { Badge } from '../common/badge'
import { MetricCard } from '../common/metric-card'
import { Grid } from '../layout/grid'
import { InlineGroup } from '../layout/inline-group'
import { MetaRow } from '../layout/meta-row'
import { ProgressBar } from './progress-bar'

type TaskStatusCardProps = {
  taskId: string
  statusLabel: string
  stageLabel: string
  statusTone: 'info' | 'success' | 'warning' | 'danger'
  currentStep: number
  totalSteps: number
  progressPercent: number
  currentStepLabel: string
  totalStepsLabel: string
  progressLabel: string
}

export function TaskStatusCard({
  currentStep,
  currentStepLabel,
  progressLabel,
  progressPercent,
  stageLabel,
  statusLabel,
  statusTone,
  taskId,
  totalSteps,
  totalStepsLabel,
}: TaskStatusCardProps) {
  return (
    <>
      <MetaRow
        left={
          <InlineGroup variant="badges">
            <Badge tone={statusTone}>{statusLabel}</Badge>
            <Badge>{stageLabel}</Badge>
          </InlineGroup>
        }
        right={<p className="mono-text">{taskId}</p>}
      />

      <ProgressBar percent={progressPercent} />

      <Grid variant="metric">
        <MetricCard label={currentStepLabel} value={currentStep} />
        <MetricCard label={totalStepsLabel} value={totalSteps} />
        <MetricCard label={progressLabel} value={`${progressPercent}%`} />
      </Grid>
    </>
  )
}
