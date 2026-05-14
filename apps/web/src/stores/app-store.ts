import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'

import type { Locale } from '../i18n/messages'

type AppStore = {
  mockMode: boolean
  locale: Locale
  setMockMode: (value: boolean) => void
  setLocale: (value: Locale) => void
}

export const useAppStore = create<AppStore>()(
  persist(
    (set) => ({
      mockMode: true,
      locale: 'en',
      setMockMode: (value) => set({ mockMode: value }),
      setLocale: (value) => set({ locale: value }),
    }),
    {
      name: 'demand-atlas-web',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        mockMode: state.mockMode,
        locale: state.locale,
      }),
    },
  ),
)
