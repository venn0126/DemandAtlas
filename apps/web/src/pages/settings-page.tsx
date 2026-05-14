import { Banner } from '../components/common/banner'
import { Card } from '../components/common/card'
import { useI18n } from '../i18n/use-i18n'

import { useAppStore } from '../stores/app-store'

export function SettingsPage() {
  const { locale, setLocale, t } = useI18n()
  const mockMode = useAppStore((state) => state.mockMode)
  const setMockMode = useAppStore((state) => state.setMockMode)

  return (
    <section className="page-section">
      <div className="page-header">
        <span className="eyebrow">{t('settings.eyebrow')}</span>
        <h1>{t('settings.title')}</h1>
        <p className="page-description">{t('settings.description')}</p>
      </div>

      <Banner title={t('settings.banner.title')} tone="warning">
        {t('settings.banner.description')}
      </Banner>

      <Card className="stack-md">
        <label className="ui-field">
          <span className="ui-field-label">{t('settings.locale.label')}</span>
          <select
            className="ui-input"
            value={locale}
            onChange={(event) => setLocale(event.target.value as 'en' | 'zh')}
          >
            <option value="en">{t('settings.locale.en')}</option>
            <option value="zh">{t('settings.locale.zh')}</option>
          </select>
        </label>
        <label className="toggle-row">
          <span>{t('common.label.mockMode')}</span>
          <input
            type="checkbox"
            checked={mockMode}
            onChange={(event) => setMockMode(event.target.checked)}
          />
        </label>
      </Card>
    </section>
  )
}
