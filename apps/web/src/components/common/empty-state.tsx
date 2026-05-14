import type { ReactNode } from 'react'

import { useI18n } from '../../i18n/use-i18n'

type EmptyStateProps = {
  title?: string
  description?: string
  action?: ReactNode
}

export function EmptyState({
  action,
  title,
  description,
}: EmptyStateProps) {
  const { t } = useI18n()

  return (
    <div className="ui-state-card">
      <div className="ui-state-icon" aria-hidden="true">
        ○
      </div>
      <h3>{title ?? t('common.empty.title')}</h3>
      <p>{description ?? t('common.empty.description')}</p>
      {action}
    </div>
  )
}
