import type { ReactNode } from 'react'

import { useI18n } from '../../i18n/use-i18n'
import { Button } from './button'

type ErrorStateProps = {
  title?: string
  description?: string
  action?: ReactNode
}

export function ErrorState({
  action,
  title,
  description,
}: ErrorStateProps) {
  const { t } = useI18n()

  return (
    <div className="ui-state-card ui-state-error">
      <div className="ui-state-icon" aria-hidden="true">
        !
      </div>
      <h3>{title ?? t('common.error.title')}</h3>
      <p>{description ?? t('common.error.description')}</p>
      {action ?? <Button variant="secondary">{t('common.error.retry')}</Button>}
    </div>
  )
}
