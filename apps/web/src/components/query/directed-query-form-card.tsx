import type { DirectedQueryViewModel } from '../../types/view-model'
import { Badge } from '../common/badge'
import { Banner } from '../common/banner'
import { Button } from '../common/button'
import { Card } from '../common/card'
import { Input } from '../common/input'
import { SelectField } from '../common/select-field'
import { InlineGroup } from '../layout/inline-group'

type DirectedQueryFormCardProps = {
  viewModel: DirectedQueryViewModel
  onKeywordsChange: (value: string) => void
  onSubredditsChange: (value: string) => void
  onRegionChange: (value: string) => void
  onSubmissionModeChange: (value: string) => void
  isSubmitting: boolean
  onSubmit: () => void
  onUseExample: () => void
}

export function DirectedQueryFormCard(props: DirectedQueryFormCardProps) {
  return (
    <Card className="stack-lg">
      <InlineGroup variant="badges">
        <Badge tone="warning">{props.viewModel.queryBadge}</Badge>
        <Badge>{props.viewModel.mockBadge}</Badge>
      </InlineGroup>

      <Input
        label={props.viewModel.keywordsLabel}
        value={props.viewModel.keywordsValue}
        onChange={(event) => props.onKeywordsChange(event.target.value)}
        hint={props.viewModel.keywordsHint}
      />
      <Input
        label={props.viewModel.subredditsLabel}
        value={props.viewModel.subredditsValue}
        onChange={(event) => props.onSubredditsChange(event.target.value)}
        hint={props.viewModel.subredditsHint}
      />
      <Input
        label={props.viewModel.regionLabel}
        value={props.viewModel.regionValue}
        onChange={(event) => props.onRegionChange(event.target.value)}
        hint={props.viewModel.regionHint}
      />
      <Input label={props.viewModel.languageLabel} value={props.viewModel.languageValue} readOnly />
      <Input label={props.viewModel.timeWindowLabel} value={props.viewModel.timeWindowValue} readOnly />
      <Input label={props.viewModel.engagementLabel} value={props.viewModel.engagementValue} readOnly />

      <SelectField
        label={props.viewModel.submissionModeLabel}
        value={props.viewModel.submissionModeValue}
        onChange={(event) => props.onSubmissionModeChange(event.target.value)}
        options={props.viewModel.submissionModeOptions}
      />

      {props.viewModel.errorMessage ? (
        <Banner title={props.viewModel.validationTitle} tone="warning">
          {props.viewModel.errorMessage}
        </Banner>
      ) : null}

      <InlineGroup variant="actions">
        <Button onClick={props.onSubmit} disabled={props.isSubmitting}>
          {props.isSubmitting
            ? props.viewModel.submittingLabel
            : props.viewModel.submitLabel}
        </Button>
        <Button variant="secondary" onClick={props.onUseExample}>
          {props.viewModel.useExampleLabel}
        </Button>
      </InlineGroup>
    </Card>
  )
}
