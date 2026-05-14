import type { ResultSnapshotSummary } from '../../types/result'
import { Badge } from '../common/badge'
import { KeyValue } from '../common/key-value'
import { MetricCard } from '../common/metric-card'
import { Grid } from '../layout/grid'
import { InlineGroup } from '../layout/inline-group'
import { MetaRow } from '../layout/meta-row'
import { Stack } from '../layout/stack'

type ResultSummaryCardProps = {
  summary: ResultSnapshotSummary
  viewTypeLabel: string
  queryTypeLabel: string
  clusterLabel: string
  postLabel: string
  commentLabel: string
  queryTaskIdLabel: string
  generatedAtLabel: string
  generatedAt: string
}

export function ResultSummaryCard(props: ResultSummaryCardProps) {
  return (
    <Stack gap="lg">
      <MetaRow
        left={
          <InlineGroup variant="badges">
              <Badge tone="success">{props.viewTypeLabel}</Badge>
              <Badge>{props.queryTypeLabel}</Badge>
            </InlineGroup>
          }
        right={<p className="mono-text">{props.summary.result_snapshot_id}</p>}
      />

      <Grid variant="metric">
        <MetricCard
          label={props.clusterLabel}
          value={props.summary.summary_stats.cluster_count}
        />
        <MetricCard label={props.postLabel} value={props.summary.summary_stats.post_count} />
        <MetricCard
          label={props.commentLabel}
          value={props.summary.summary_stats.comment_count}
        />
      </Grid>

      <Stack gap="md">
        <KeyValue label={props.queryTaskIdLabel} value={props.summary.query_task_id} />
        <KeyValue label={props.generatedAtLabel} value={props.generatedAt} />
      </Stack>
    </Stack>
  )
}
