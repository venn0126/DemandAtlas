import { Banner } from '../components/common/banner'
import { Card } from '../components/common/card'
import { EmptyState } from '../components/common/empty-state'
import { ErrorState } from '../components/common/error-state'
import { LoadingState } from '../components/common/loading-state'
import { Tabs } from '../components/common/tabs'
import { Grid } from '../components/layout/grid'
import { MetaRow } from '../components/layout/meta-row'
import { Page } from '../components/layout/page'
import { PageHeader } from '../components/layout/page-header'
import { useResultPage } from '../hooks/use-result-page'
import { ResultBoardItem } from '../components/result/result-board-item'
import { ResultSummaryCard } from '../components/result/result-summary-card'

export function ResultPage() {
  const vm = useResultPage()

  return (
    <Page>
      <PageHeader
        eyebrow={vm.eyebrow}
        title={vm.title}
        description={vm.description}
      />

      {vm.summaryQuery.isLoading ? (
        <LoadingState title={vm.labels.loadingSummary} />
      ) : null}
      {vm.summaryQuery.isError ? (
        <ErrorState
          title={vm.labels.errorSummaryTitle}
          description={vm.labels.errorSummaryDescription}
        />
      ) : null}

      {vm.summary ? (
        <>
          <Card className="stack-lg">
            <ResultSummaryCard
              summary={vm.summary}
              viewTypeLabel={vm.summary.view_type}
              queryTypeLabel={vm.summary.query_type}
              clusterLabel={vm.labels.clusterLabel}
              postLabel={vm.labels.postLabel}
              commentLabel={vm.labels.commentLabel}
              queryTaskIdLabel={vm.labels.queryTaskIdLabel}
              generatedAtLabel={vm.labels.generatedAtLabel}
              generatedAt={vm.labels.generatedAtValue}
            />
          </Card>

          {vm.summary.coverage_note ? (
            <Banner title={vm.labels.coverageTitle} tone="warning">
              {vm.summary.coverage_note}
            </Banner>
          ) : null}

          <Banner title={vm.labels.freshnessTitle} tone="info">
            {vm.summary.sync_freshness_note}
          </Banner>

          <Card className="stack-lg">
            <MetaRow
              left={
                <Tabs
                  value={vm.activeBoard}
                  onChange={(value) => vm.setActiveBoard(value)}
                  items={vm.boardTabOptions.map((item) => ({
                    key: item.value,
                    label: item.label,
                  }))}
                />
              }
            />

            {vm.boardQuery.isLoading ? (
              <LoadingState title={vm.labels.loadingBoard} />
            ) : null}
            {vm.boardQuery.isError ? (
              <ErrorState
                title={vm.labels.errorBoardTitle}
                description={vm.labels.errorBoardDescription}
              />
            ) : null}

            {vm.board?.items.length ? (
              <Grid variant="result">
                {vm.boardItems.map((item) => (
                  <ResultBoardItem
                    key={item.clusterId}
                    resultSnapshotId={vm.resultSnapshotId ?? ''}
                    item={item}
                    emergingLabel={vm.labels.emerging}
                    lowConfidenceLabel={vm.labels.lowConfidence}
                    weakSignalLabel={vm.labels.weakSignal}
                  />
                ))}
              </Grid>
            ) : (
              <EmptyState
                title={vm.labels.emptyTitle}
                description={vm.labels.emptyDescription}
              />
            )}
          </Card>
        </>
      ) : null}
    </Page>
  )
}
