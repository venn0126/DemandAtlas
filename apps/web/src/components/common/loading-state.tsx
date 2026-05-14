import { useI18n } from '../../i18n/use-i18n'

type LoadingStateProps = {
  title?: string
  description?: string
}

export function LoadingState({
  title,
  description,
}: LoadingStateProps) {
  const { t } = useI18n()

  return (
    <div className="ui-state-card">
      <div className="ui-spinner" aria-hidden="true" />
      <h3>{title ?? t('common.loading.title')}</h3>
      <p>{description ?? t('common.loading.description')}</p>
    </div>
  )
}
