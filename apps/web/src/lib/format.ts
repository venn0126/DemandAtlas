import type { Locale } from '../i18n/messages'

export function toIntlLocale(locale: Locale) {
  return locale === 'zh' ? 'zh-CN' : 'en-US'
}

export function formatUtcDateTime(value: string, locale: Locale) {
  return new Intl.DateTimeFormat(toIntlLocale(locale), {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short',
  }).format(new Date(value))
}
