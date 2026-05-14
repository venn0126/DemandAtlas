import { Banner } from '../components/common/banner'
import { Card } from '../components/common/card'
import { ErrorState } from '../components/common/error-state'
import { LoadingState } from '../components/common/loading-state'
import { DetailContextCard } from '../components/detail/detail-context-card'
import { DetailMetricsCard } from '../components/detail/detail-metrics-card'
import { DetailOverviewCard } from '../components/detail/detail-overview-card'
import { useDetailPage } from '../hooks/use-detail-page'
import { Page } from '../components/layout/page'
import { PageHeader } from '../components/layout/page-header'
import { Stack } from '../components/layout/stack'
import { EvidenceCard } from '../components/result/evidence-card'

export function ClusterDetailPage() {
  const vm = useDetailPage()

  return (
    <Page>
      <PageHeader
        eyebrow={vm.eyebrow}
        title={vm.title}
        description={vm.description}
      />

      {vm.detailQuery.isLoading ? (
        <LoadingState title={vm.labels.loadingTitle} />
      ) : null}
      {vm.detailQuery.isError ? (
        <ErrorState
          title={vm.labels.errorTitle}
          description={vm.labels.errorDescription}
        />
      ) : null}

      {vm.detail ? (
        <>
          <Card className="stack-lg">
            <DetailOverviewCard
              resultSnapshotId={vm.resultSnapshotId}
              detail={vm.detail}
              resultSnapshotLabel={vm.labels.overview.resultSnapshotLabel}
              timeWindowLabel={vm.labels.overview.timeWindowLabel}
              timeWindowValue={vm.labels.overview.timeWindowValue}
              emergingLabel={vm.labels.overview.emergingLabel}
              lowConfidenceLabel={vm.labels.overview.lowConfidenceLabel}
              weakSignalLabel={vm.labels.overview.weakSignalLabel}
              isEmergingSignal={vm.detail.flags.is_emerging_signal}
              isLowConfidence={vm.detail.flags.is_low_confidence}
              isWeakSignal={vm.detail.flags.is_weak_signal}
              scores={vm.scoreRows}
            />
          </Card>

          {vm.detail.coverage_note ? (
            <Banner title={vm.labels.coverageTitle} tone="warning">
              {vm.detail.coverage_note}
            </Banner>
          ) : null}

          <Card className="stack-lg">
            <DetailMetricsCard
              title={vm.labels.metrics.title}
              metricLabels={{
                posts: vm.labels.metrics.posts,
                comments: vm.labels.metrics.comments,
                users: vm.labels.metrics.users,
                communities: vm.labels.metrics.communities,
              }}
              metrics={vm.detail.metrics}
            />
          </Card>

          <Card className="stack-lg">
            <DetailContextCard
              title={vm.labels.context.title}
              scenesLabel={vm.labels.context.scenes}
              painPointsLabel={vm.labels.context.painPoints}
              alternativesLabel={vm.labels.context.alternatives}
              detail={vm.detail}
            />
          </Card>

          <Card className="stack-lg">
            <h2>{vm.labels.evidence.supporting}</h2>
            <Stack gap="md">
              {vm.detail.supporting_evidence.map((item) => (
                <EvidenceCard
                  key={item.evidence_id}
                  excerpt={item.excerpt}
                  subreddit={item.subreddit}
                  createdAt={item.created_at}
                  availabilityStatus={item.availability_status}
                  sourceUrl={item.source_url}
                />
              ))}
            </Stack>
          </Card>

          {vm.detail.opposing_evidence.length ? (
            <Card className="stack-lg">
              <h2>{vm.labels.evidence.opposing}</h2>
              <Stack gap="md">
                {vm.detail.opposing_evidence.map((item) => (
                  <EvidenceCard
                    key={item.evidence_id}
                    excerpt={item.excerpt}
                    subreddit={item.subreddit}
                    createdAt={item.created_at}
                    availabilityStatus={item.availability_status}
                    sourceUrl={item.source_url}
                  />
                ))}
              </Stack>
            </Card>
          ) : null}
        </>
      ) : null}
    </Page>
  )
}
