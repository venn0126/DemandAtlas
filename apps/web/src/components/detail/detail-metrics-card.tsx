import type { DetailMetrics } from '../../types/detail'
import { MetricCard } from '../common/metric-card'
import { Grid } from '../layout/grid'
import { Stack } from '../layout/stack'

type DetailMetricsCardProps = {
  title: string
  metricLabels: {
    posts: string
    comments: string
    users: string
    communities: string
  }
  metrics: DetailMetrics
}

export function DetailMetricsCard({ metricLabels, metrics, title }: DetailMetricsCardProps) {
  return (
    <Stack gap="lg">
      <h2>{title}</h2>
      <Grid variant="metric">
        <MetricCard label={metricLabels.posts} value={metrics.post_count} />
        <MetricCard label={metricLabels.comments} value={metrics.comment_count} />
        <MetricCard label={metricLabels.users} value={metrics.unique_user_count} />
        <MetricCard
          label={metricLabels.communities}
          value={metrics.community_spread_count}
        />
      </Grid>
    </Stack>
  )
}
