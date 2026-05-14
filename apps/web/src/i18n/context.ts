import { createContext } from 'react'

import type { Locale, TranslationKey } from './messages'

type TranslationValues = Record<string, string | number>

export type I18nContextValue = {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: TranslationKey, values?: TranslationValues) => string
  tDynamic: (prefix: string, value: string | null | undefined) => string
}

export const I18nContext = createContext<I18nContextValue | null>(null)
