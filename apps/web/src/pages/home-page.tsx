import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { routes } from '../app/routes'
import { Badge } from '../components/common/badge'
import { Banner } from '../components/common/banner'
import { Button } from '../components/common/button'
import { Card } from '../components/common/card'
import { ErrorState } from '../components/common/error-state'
import { LoadingState } from '../components/common/loading-state'
import { HomeTemplateCard } from '../components/home/home-template-card'
import { Grid } from '../components/layout/grid'
import { InlineGroup } from '../components/layout/inline-group'
import { Page } from '../components/layout/page'
import { PageHeader } from '../components/layout/page-header'
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
    <Page>
      <PageHeader
        eyebrow="Sprint 01 / FE-01"
        title={t('home.title')}
        description={t('home.description')}
      />

      <Banner title={t('home.banner.title')} tone="info">
        {t('home.banner.description')}
      </Banner>

      <InlineGroup variant="actions">
        <Link to={routes.oneClick}>
          <Button>{t('home.actions.oneClick')}</Button>
        </Link>
        <Link to={routes.directed}>
          <Button variant="secondary">{t('home.actions.directed')}</Button>
        </Link>
      </InlineGroup>

      <Grid variant="panel">
        <Card>
          <h2>{t('home.currentScope.title')}</h2>
          <InlineGroup variant="badges">
            <Badge tone="success">{t('home.currentScope.routerReady')}</Badge>
            <Badge tone="info">{t('home.currentScope.mockReady')}</Badge>
          </InlineGroup>
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
            <Grid variant="template">
              {templateQuery.data.data.items.map((item) => (
                  <HomeTemplateCard
                    key={item.template_id}
                    template={item}
                    viewTypeLabel={tDynamic('enum.viewType', item.default_view_type)}
                  />
              ))}
            </Grid>
          ) : null}
        </Card>
      </Grid>
    </Page>
  )
}
