import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { Badge } from '../components/common/badge'
import { Banner } from '../components/common/banner'
import { Button } from '../components/common/button'
import { Card } from '../components/common/card'
import { ErrorState } from '../components/common/error-state'
import { LoadingState } from '../components/common/loading-state'
import { useI18n } from '../i18n/use-i18n'
import { queryKeys } from '../lib/query-keys'
import { listTopicTemplates } from '../services/mock-api'

export function HomePage() {
  const { t, tDynamic } = useI18n()
  const templateQuery = useQuery({
    queryKey: queryKeys.topicTemplates,
    queryFn: listTopicTemplates,
  })

  return (
    <section className="page-section">
      <div className="page-header">
        <span className="eyebrow">Sprint 01 / FE-01</span>
        <h1>{t('home.title')}</h1>
        <p className="page-description">{t('home.description')}</p>
      </div>

      <Banner title={t('home.banner.title')} tone="info">
        {t('home.banner.description')}
      </Banner>

      <div className="page-actions">
        <Link to="/discover/one-click">
          <Button>{t('home.actions.oneClick')}</Button>
        </Link>
        <Link to="/discover/directed">
          <Button variant="secondary">{t('home.actions.directed')}</Button>
        </Link>
      </div>

      <div className="panel-grid">
        <Card>
          <h2>{t('home.currentScope.title')}</h2>
          <div className="badge-row">
            <Badge tone="success">{t('home.currentScope.routerReady')}</Badge>
            <Badge tone="info">{t('home.currentScope.mockReady')}</Badge>
          </div>
          <ul className="bullet-list">
            <li>{t('home.currentScope.item.router')}</li>
            <li>{t('home.currentScope.item.appShell')}</li>
            <li>{t('home.currentScope.item.query')}</li>
            <li>{t('home.currentScope.item.mockAdapter')}</li>
          </ul>
        </Card>

        <Card>
          <h2>{t('home.templates.title')}</h2>
          {templateQuery.isLoading ? <LoadingState title={t('home.templates.loading')} /> : null}
          {templateQuery.isError ? (
            <ErrorState
              title={t('home.templates.errorTitle')}
              description={t('home.templates.errorDescription')}
            />
          ) : null}
          {templateQuery.data?.data.items?.length ? (
            <div className="template-grid">
              {templateQuery.data.data.items.map((item) => (
                <Link
                  key={item.template_id}
                  to={`/discover/one-click?templateId=${item.template_id}`}
                  className="template-link"
                >
                  <div className="template-card">
                    <div className="badge-row">
                      <Badge tone="info">
                        {tDynamic('enum.viewType', item.default_view_type)}
                      </Badge>
                      <Badge>{item.default_language}</Badge>
                    </div>
                    <h3>{item.name}</h3>
                    <p>{item.description}</p>
                  </div>
                </Link>
              ))}
            </div>
          ) : null}
        </Card>
      </div>
    </section>
  )
}
