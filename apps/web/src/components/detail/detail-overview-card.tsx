import { Badge } from '../common/badge'
import { KeyValue } from '../common/key-value'
import { Grid } from '../layout/grid'
import { InlineGroup } from '../layout/inline-group'
import { MetaRow } from '../layout/meta-row'
import { Stack } from '../layout/stack'
import { ScorePill } from '../result/score-pill'
import type { ClusterDetail } from '../../types/detail'

type DetailOverviewCardProps = {
  resultSnapshotId?: string
  detail: ClusterDetail
  timeWindowLabel: string
  timeWindowValue: string
  resultSnapshotLabel: string
  emergingLabel?: string
  lowConfidenceLabel?: string
  weakSignalLabel?: string
  isEmergingSignal: boolean
  isLowConfidence: boolean
  isWeakSignal: boolean
  scores: Array<{
    label: string
    value: number
  }>
}

export function DetailOverviewCard(props: DetailOverviewCardProps) {
  return (
    <Stack gap="lg">
      <MetaRow
        left={
          <InlineGroup variant="badges">
            {props.isEmergingSignal && props.emergingLabel ? (
              <Badge tone="info">{props.emergingLabel}</Badge>
            ) : null}
            {props.isLowConfidence && props.lowConfidenceLabel ? (
              <Badge tone="warning">{props.lowConfidenceLabel}</Badge>
            ) : null}
            {props.isWeakSignal && props.weakSignalLabel ? (
              <Badge tone="warning">{props.weakSignalLabel}</Badge>
            ) : null}
          </InlineGroup>
        }
        right={<p className="mono-text">{props.resultSnapshotId}</p>}
      />

      <div>
        <h2>{props.detail.title}</h2>
        <p>{props.detail.summary}</p>
        <KeyValue label={props.resultSnapshotLabel} value={props.resultSnapshotId} />
        <KeyValue label={props.timeWindowLabel} value={props.timeWindowValue} />
      </div>

      <Grid variant="score">
        {props.scores.map((item) => (
          <ScorePill key={item.label} label={item.label} value={item.value} />
        ))}
      </Grid>
    </Stack>
  )
}
