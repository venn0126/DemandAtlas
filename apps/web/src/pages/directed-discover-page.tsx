import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { Badge } from '../components/common/badge'
import { Banner } from '../components/common/banner'
import { Button } from '../components/common/button'
import { Card } from '../components/common/card'
import { Input } from '../components/common/input'
import { useI18n } from '../i18n/use-i18n'
import { saveAnonymousQuerySession } from '../lib/anonymous-query-session'
import { createQueryTask } from '../services/mock-api'

export function DirectedDiscoverPage() {
  const { locale, t, tDynamic } = useI18n()
  const navigate = useNavigate()
  const [keywords, setKeywords] = useState('reddit growth pain point')
  const [subreddits, setSubreddits] = useState('r/Entrepreneur, r/SaaS')
  const [regionHint, setRegionHint] = useState('US')
  const [submissionMode, setSubmissionMode] = useState<'async' | 'cache-hit' | 'too-broad'>(
    'async',
  )
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit() {
    setErrorMessage(null)
    setIsSubmitting(true)

    try {
      const response = await createQueryTask(submissionMode)
      const payload = response.data

      if (response.error?.message) {
        setErrorMessage(
          response.error.code === 'QUERY_TOO_BROAD'
            ? t('directed.validation.tooBroadMessage')
            : response.error.message,
        )
        return
      }

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
        <span className="eyebrow">{t('directed.eyebrow')}</span>
        <h1>{t('directed.title')}</h1>
        <p className="page-description">{t('directed.description')}</p>
      </div>

      <Card className="stack-lg">
        <div className="badge-row">
          <Badge tone="warning">{t('directed.badge.query')}</Badge>
          <Badge>{t('directed.badge.mock')}</Badge>
        </div>
        <Input
          label={t('directed.form.keywords.label')}
          value={keywords}
          onChange={(event) => setKeywords(event.target.value)}
          hint={t('directed.form.keywords.hint')}
        />
        <Input
          label={t('directed.form.subreddits.label')}
          value={subreddits}
          onChange={(event) => setSubreddits(event.target.value)}
          hint={t('directed.form.subreddits.hint')}
        />
        <Input
          label={t('directed.form.region.label')}
          value={regionHint}
          onChange={(event) => setRegionHint(event.target.value)}
          hint={t('directed.form.region.hint')}
        />
        <Input label={t('directed.form.language')} value="en" readOnly />
        <Input label={t('directed.form.timeWindow')} value={t('common.value.last30Days')} readOnly />
        <Input label={t('directed.form.engagement')} value={t('common.value.basic')} readOnly />
        <label className="ui-field">
          <span className="ui-field-label">{t('directed.form.submissionMode')}</span>
          <select
            className="ui-input"
            value={submissionMode}
            onChange={(event) =>
              setSubmissionMode(event.target.value as 'async' | 'cache-hit' | 'too-broad')
            }
          >
            <option value="async">{tDynamic('enum.submissionMode', 'async')}</option>
            <option value="cache-hit">{tDynamic('enum.submissionMode', 'cache-hit')}</option>
            <option value="too-broad">{tDynamic('enum.submissionMode', 'too-broad')}</option>
          </select>
        </label>
        {errorMessage ? (
          <Banner title={t('directed.validation.title')} tone="warning">
            {errorMessage}
          </Banner>
        ) : null}
        <div className="page-actions">
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? t('directed.actions.submitting') : t('directed.actions.submit')}
          </Button>
          <Button
            variant="secondary"
            onClick={() => {
              setKeywords('AI assistant workflow')
              setSubreddits('r/ChatGPT, r/OpenAI')
              setRegionHint(locale === 'zh' ? '全球' : 'Global')
              setErrorMessage(null)
            }}
          >
            {t('directed.actions.useExample')}
          </Button>
        </div>
      </Card>
    </section>
  )
}
