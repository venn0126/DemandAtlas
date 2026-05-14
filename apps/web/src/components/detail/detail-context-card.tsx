import type { ClusterDetail } from '../../types/detail'
import { Badge } from '../common/badge'
import { InlineGroup } from '../layout/inline-group'
import { SectionBlock } from '../layout/section-block'
import { Stack } from '../layout/stack'

type DetailContextCardProps = {
  title: string
  scenesLabel: string
  painPointsLabel: string
  alternativesLabel: string
  detail: ClusterDetail
}

export function DetailContextCard({
  alternativesLabel,
  painPointsLabel,
  scenesLabel,
  detail,
  title,
}: DetailContextCardProps) {
  return (
    <Stack gap="lg">
      <h2>{title}</h2>
      <Stack gap="md">
        <SectionBlock title={scenesLabel} titleClassName="section-label">
          <InlineGroup variant="badges">
            {detail.scenes.map((scene) => (
              <Badge key={scene}>{scene}</Badge>
            ))}
          </InlineGroup>
        </SectionBlock>
        <SectionBlock title={painPointsLabel} titleClassName="section-label">
          <InlineGroup variant="badges">
            {detail.pain_points.map((item) => (
              <Badge key={item} tone="warning">
                {item}
              </Badge>
            ))}
          </InlineGroup>
        </SectionBlock>
        <SectionBlock title={alternativesLabel} titleClassName="section-label">
          <InlineGroup variant="badges">
            {detail.alternatives.map((item) => (
              <Badge key={item} tone="info">
                {item}
              </Badge>
            ))}
          </InlineGroup>
        </SectionBlock>
      </Stack>
    </Stack>
  )
}
