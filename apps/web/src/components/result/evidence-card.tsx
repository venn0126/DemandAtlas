import { useI18n } from '../../i18n/use-i18n'
import { formatUtcDateTime } from '../../lib/format'

type EvidenceCardProps = {
  excerpt: string
  subreddit: string
  createdAt: string
  availabilityStatus: string
  sourceUrl: string | null
}

export function EvidenceCard({
  availabilityStatus,
  createdAt,
  excerpt,
  sourceUrl,
  subreddit,
}: EvidenceCardProps) {
  const { locale, t, tDynamic } = useI18n()

  return (
    <article className="evidence-card">
      <div className="badge-row">
        <span className="ui-badge ui-badge-neutral">{subreddit}</span>
        <span className="ui-badge ui-badge-info">
          {tDynamic('enum.availability', availabilityStatus)}
        </span>
      </div>
      <p>{excerpt}</p>
      <div className="evidence-meta">
        <span>{formatUtcDateTime(createdAt, locale)}</span>
        {sourceUrl ? (
          <a href={sourceUrl} target="_blank" rel="noreferrer">
            {t('evidence.openSource')}
          </a>
        ) : (
          <span>{t('evidence.unavailable')}</span>
        )}
      </div>
    </article>
  )
}
