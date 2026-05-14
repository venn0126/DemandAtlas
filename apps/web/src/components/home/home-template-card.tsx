import { Link } from 'react-router-dom'

import { routeBuilders } from '../../app/routes'
import type { TopicTemplateListItem } from '../../types/query'
import { Badge } from '../common/badge'
import { InlineGroup } from '../layout/inline-group'

type HomeTemplateCardProps = {
  template: TopicTemplateListItem
  viewTypeLabel: string
}

export function HomeTemplateCard({ template, viewTypeLabel }: HomeTemplateCardProps) {
  return (
    <Link
      to={routeBuilders.oneClickWithTemplate(template.template_id)}
      className="template-link"
    >
      <div className="template-card">
        <InlineGroup variant="badges">
          <Badge tone="info">{viewTypeLabel || template.default_view_type}</Badge>
          <Badge>{template.default_language}</Badge>
        </InlineGroup>
        <h3>{template.name}</h3>
        <p>{template.description}</p>
      </div>
    </Link>
  )
}
