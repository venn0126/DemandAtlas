import type { OneClickQueryViewModel } from '../../types/view-model'
import { Badge } from '../common/badge'
import { Banner } from '../common/banner'
import { Button } from '../common/button'
import { Card } from '../common/card'
import { ErrorState } from '../common/error-state'
import { Input } from '../common/input'
import { LoadingState } from '../common/loading-state'
import { SelectField } from '../common/select-field'
import { InlineGroup } from '../layout/inline-group'

type OneClickQueryCardProps = {
  viewModel: OneClickQueryViewModel
  isLoading: boolean
  isError: boolean
  onTemplateChange: (value: string) => void
  onSubmissionModeChange: (value: string) => void
  isSubmitting: boolean
  onSubmit: () => void
  onToggleMode: () => void
}

export function OneClickQueryCard(props: OneClickQueryCardProps) {
  return (
    <Card className="stack-lg">
      <InlineGroup variant="badges">
        <Badge tone="info">{props.viewModel.templateBadge}</Badge>
        <Badge>{props.viewModel.mockBadge}</Badge>
      </InlineGroup>

      {props.isLoading ? <LoadingState title={props.viewModel.loadingTitle} /> : null}
      {props.isError ? (
        <ErrorState
          title={props.viewModel.errorTitle}
          description={props.viewModel.errorDescription}
        />
      ) : null}

      {props.viewModel.templateOptions.length ? (
        <SelectField
          label={props.viewModel.templateLabel}
          value={props.viewModel.templateValue}
          onChange={(event) => props.onTemplateChange(event.target.value)}
          options={props.viewModel.templateOptions}
        />
      ) : null}

      <Input
        label={props.viewModel.timeWindowLabel}
        value={props.viewModel.timeWindowValue}
        readOnly
      />
      <Input
        label={props.viewModel.viewTypeLabel}
        value={props.viewModel.viewTypeValue}
        readOnly
      />

      {props.viewModel.detailBannerTitle && props.viewModel.detailBannerDescription ? (
        <Banner title={props.viewModel.detailBannerTitle} tone="info">
          {props.viewModel.detailBannerDescription}
        </Banner>
      ) : null}

      <SelectField
        label={props.viewModel.submissionModeLabel}
        value={props.viewModel.submissionModeValue}
        onChange={(event) => props.onSubmissionModeChange(event.target.value)}
        options={props.viewModel.submissionModeOptions}
      />

      <InlineGroup variant="actions">
        <Button onClick={props.onSubmit} disabled={props.isSubmitting}>
          {props.isSubmitting
            ? props.viewModel.submittingLabel
            : props.viewModel.submitLabel}
        </Button>
        <Button variant="secondary" onClick={props.onToggleMode}>
          {props.viewModel.toggleModeLabel}
        </Button>
      </InlineGroup>
    </Card>
  )
}
