import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { Badge } from '../components/common/badge'
import { Banner } from '../components/common/banner'
import { Button } from '../components/common/button'
import { Card } from '../components/common/card'
import { ErrorState } from '../components/common/error-state'
import { Input } from '../components/common/input'
import { LoadingState } from '../components/common/loading-state'
import { useI18n } from '../i18n/use-i18n'
import { saveAnonymousQuerySession } from '../lib/anonymous-query-session'
import { queryKeys } from '../lib/query-keys'
import { createQueryTask, getTopicTemplateDetail, listTopicTemplates } from '../services/mock-api'

export function OneClickDiscoverPage() {
  const { t, tDynamic } = useI18n()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [templateId, setTemplateId] = useState(searchParams.get('templateId') ?? 'tpl_ai_tools')
  const [submitMode, setSubmitMode] = useState<'async' | 'cache-hit'>('async')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const templateListQuery = useQuery({
    queryKey: queryKeys.topicTemplates,
    queryFn: listTopicTemplates,
  })

  const templateDetailQuery = useQuery({
    queryKey: queryKeys.topicTemplateDetail(templateId),
    queryFn: getTopicTemplateDetail,
  })

  async function handleSubmit() {
    setIsSubmitting(true)

    try {
      const response = await createQueryTask(submitMode)
      const payload = response.data

      if (payload && 'result_snapshot_id' in payload) {
        navigate(`/results/${payload.result_snapshot_id}`)
        return
      }

      if (payload && 'query_task_id' in payload) {
        if ('anonymous_query_access_token' in payload) {
          saveAnonymousQuerySession({
            queryTaskId: payload.query_task_id,
            token: payload.anonymous_query_access_token,
            createdAt: new Date().toISOString(),
          })
        }

        navigate(`/tasks/${payload.query_task_id}`)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="page-section">
      <div className="page-header">
        <span className="eyebrow">{t('oneClick.eyebrow')}</span>
        <h1>{t('oneClick.title')}</h1>
        <p className="page-description">{t('oneClick.description')}</p>
      </div>

      <Card className="stack-lg">
        <div className="badge-row">
          <Badge tone="info">{t('oneClick.badge.template')}</Badge>
          <Badge>{t('oneClick.badge.mock')}</Badge>
        </div>
        {templateListQuery.isLoading ? (
          <LoadingState title={t('oneClick.loadingTemplates')} />
        ) : null}
        {templateListQuery.isError ? (
          <ErrorState
            title={t('oneClick.errorTemplatesTitle')}
            description={t('oneClick.errorTemplatesDescription')}
          />
        ) : null}
        {templateListQuery.data?.data.items?.length ? (
          <label className="ui-field">
            <span className="ui-field-label">{t('oneClick.form.template')}</span>
            <select
              className="ui-input"
              value={templateId}
              onChange={(event) => setTemplateId(event.target.value)}
            >
              {templateListQuery.data.data.items.map((item) => (
                <option key={item.template_id} value={item.template_id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
        ) : null}
        <Input
          label={t('oneClick.form.timeWindow')}
          value={t('common.value.last30Days')}
          readOnly
        />
        <Input
          label={t('oneClick.form.viewType')}
          value={tDynamic('enum.viewType', 'active')}
          readOnly
        />
        {templateDetailQuery.data?.data ? (
          <Banner title={templateDetailQuery.data.data.name} tone="info">
            {t('oneClick.banner.summary', {
              description: templateDetailQuery.data.data.description,
              count: templateDetailQuery.data.data.candidate_subreddit_count,
            })}
          </Banner>
        ) : null}
        <label className="ui-field">
          <span className="ui-field-label">{t('oneClick.form.submissionMode')}</span>
          <select
            className="ui-input"
            value={submitMode}
            onChange={(event) => setSubmitMode(event.target.value as 'async' | 'cache-hit')}
          >
            <option value="async">{tDynamic('enum.submissionMode', 'async')}</option>
            <option value="cache-hit">{tDynamic('enum.submissionMode', 'cache-hit')}</option>
          </select>
        </label>
        <div className="page-actions">
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? t('oneClick.actions.submitting') : t('oneClick.actions.run')}
          </Button>
          <Button
            variant="secondary"
            onClick={() => setSubmitMode(submitMode === 'async' ? 'cache-hit' : 'async')}
          >
            {t('oneClick.actions.toggleMode')}
          </Button>
        </div>
      </Card>
    </section>
  )
}
