import { useEffect, useMemo, type ReactNode } from 'react'

import { useAppStore } from '../stores/app-store'
import { messages, type TranslationKey } from './messages'
import { I18nContext, type I18nContextValue } from './context'

type TranslationValues = Record<string, string | number>

function formatMessage(template: string, values?: TranslationValues) {
  if (!values) {
    return template
  }

  return template.replace(/\{(\w+)\}/g, (_, key: string) => String(values[key] ?? `{${key}}`))
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const locale = useAppStore((state) => state.locale)
  const setLocale = useAppStore((state) => state.setLocale)

  useEffect(() => {
    document.documentElement.lang = locale === 'zh' ? 'zh-CN' : 'en'
  }, [locale])

  const value = useMemo<I18nContextValue>(
    () => ({
      locale,
      setLocale,
      t: (key, values) => formatMessage(messages[locale][key] ?? messages.en[key], values),
      tDynamic: (prefix, rawValue) => {
        if (!rawValue) {
          return ''
        }

        const key = `${prefix}.${rawValue}` as TranslationKey
        return messages[locale][key] ?? messages.en[key] ?? rawValue
      },
    }),
    [locale, setLocale],
  )

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}
