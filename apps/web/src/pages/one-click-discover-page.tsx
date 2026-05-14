import { Page } from '../components/layout/page'
import { PageHeader } from '../components/layout/page-header'
import { OneClickQueryCard } from '../components/query/one-click-query-card'
import { useOneClickQueryPage } from '../hooks/use-one-click-query-page'

export function OneClickDiscoverPage() {
  const vm = useOneClickQueryPage()

  return (
    <Page>
      <PageHeader
        eyebrow={vm.eyebrow}
        title={vm.title}
        description={vm.description}
      />

      <OneClickQueryCard
        viewModel={vm.viewModel}
        isLoading={vm.isLoading}
        isError={vm.isError}
        onTemplateChange={vm.setTemplateId}
        onSubmissionModeChange={(value) =>
          vm.setSubmitMode(value as 'async' | 'cache-hit')
        }
        isSubmitting={vm.isSubmitting}
        onSubmit={vm.handleSubmit}
        onToggleMode={() =>
          vm.setSubmitMode(
            vm.viewModel.submissionModeValue === 'async' ? 'cache-hit' : 'async',
          )
        }
      />
    </Page>
  )
}
