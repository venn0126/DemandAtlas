import { Banner } from '../components/common/banner'
import { Card } from '../components/common/card'
import { SelectField } from '../components/common/select-field'
import { Page } from '../components/layout/page'
import { PageHeader } from '../components/layout/page-header'
import { Stack } from '../components/layout/stack'
import { useI18n } from '../i18n/use-i18n'

import { useAppStore } from '../stores/app-store'

export function SettingsPage() {
  const { locale, setLocale, t } = useI18n()
  const mockMode = useAppStore((state) => state.mockMode)
  const setMockMode = useAppStore((state) => state.setMockMode)

  return (
    <Page>
      <PageHeader
        eyebrow={t('settings.eyebrow')}
        title={t('settings.title')}
        description={t('settings.description')}
      />

      <Banner title={t('settings.banner.title')} tone="warning">
        {t('settings.banner.description')}
      </Banner>

      <Card>
        <Stack gap="md">
          <SelectField
            label={t('settings.locale.label')}
            value={locale}
            onChange={(event) => setLocale(event.target.value as 'en' | 'zh')}
            options={[
              { value: 'en', label: t('settings.locale.en') },
              { value: 'zh', label: t('settings.locale.zh') },
            ]}
          />
          <label className="toggle-row">
            <span>{t('common.label.mockMode')}</span>
            <input
              type="checkbox"
              checked={mockMode}
              onChange={(event) => setMockMode(event.target.checked)}
            />
          </label>
        </Stack>
      </Card>
    </Page>
  )
}
