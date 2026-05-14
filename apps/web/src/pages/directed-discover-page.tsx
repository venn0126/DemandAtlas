import { Page } from '../components/layout/page'
import { PageHeader } from '../components/layout/page-header'
import { DirectedQueryFormCard } from '../components/query/directed-query-form-card'
import { useDirectedQueryPage } from '../hooks/use-directed-query-page'

export function DirectedDiscoverPage() {
  const vm = useDirectedQueryPage()

  return (
    <Page>
      <PageHeader
        eyebrow={vm.eyebrow}
        title={vm.title}
        description={vm.description}
      />

      <DirectedQueryFormCard
        viewModel={vm.viewModel}
        onKeywordsChange={vm.setKeywords}
        onSubredditsChange={vm.setSubreddits}
        onRegionChange={vm.setRegionHint}
        onSubmissionModeChange={(value) => vm.setSubmissionMode(value as 'async' | 'cache-hit' | 'too-broad')}
        isSubmitting={vm.isSubmitting}
        onSubmit={vm.handleSubmit}
        onUseExample={vm.handleUseExample}
      />
    </Page>
  )
}
