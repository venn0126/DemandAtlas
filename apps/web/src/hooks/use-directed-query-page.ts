import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { toDirectedQueryViewModel } from '../adapters/query'
import { routeBuilders } from '../app/routes'
import { useI18n } from '../i18n/use-i18n'
import { saveAnonymousQuerySession } from '../lib/anonymous-query-session'
import { createQueryTask } from '../services/mock-api'
import type { SelectMode } from '../types/common'

export function useDirectedQueryPage() {
  const { locale, t, tDynamic } = useI18n()
  const navigate = useNavigate()
  const [keywords, setKeywords] = useState('reddit growth pain point')
  const [subreddits, setSubreddits] = useState('r/Entrepreneur, r/SaaS')
  const [regionHint, setRegionHint] = useState('US')
  const [submissionMode, setSubmissionMode] = useState<SelectMode>('async')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const viewModel = toDirectedQueryViewModel({
    queryBadge: t('directed.badge.query'),
    mockBadge: t('directed.badge.mock'),
    keywordsLabel: t('directed.form.keywords.label'),
    keywordsValue: keywords,
    keywordsHint: t('directed.form.keywords.hint'),
    subredditsLabel: t('directed.form.subreddits.label'),
    subredditsValue: subreddits,
    subredditsHint: t('directed.form.subreddits.hint'),
    regionLabel: t('directed.form.region.label'),
    regionValue: regionHint,
    regionHint: t('directed.form.region.hint'),
    languageLabel: t('directed.form.language'),
    languageValue: 'en',
    timeWindowLabel: t('directed.form.timeWindow'),
    timeWindowValue: t('common.value.last30Days'),
    engagementLabel: t('directed.form.engagement'),
    engagementValue: t('common.value.basic'),
    submissionModeLabel: t('directed.form.submissionMode'),
    submissionModeValue: submissionMode,
    submissionModeOptions: [
      { value: 'async', label: tDynamic('enum.submissionMode', 'async') },
      { value: 'cache-hit', label: tDynamic('enum.submissionMode', 'cache-hit') },
      { value: 'too-broad', label: tDynamic('enum.submissionMode', 'too-broad') },
    ],
    validationTitle: t('directed.validation.title'),
    errorMessage,
    submitLabel: t('directed.actions.submit'),
    submittingLabel: t('directed.actions.submitting'),
    useExampleLabel: t('directed.actions.useExample'),
  })

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
        navigate(routeBuilders.result(payload.result_snapshot_id))
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

        navigate(routeBuilders.task(payload.query_task_id))
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  function handleUseExample() {
    setKeywords('AI assistant workflow')
    setSubreddits('r/ChatGPT, r/OpenAI')
    setRegionHint(locale === 'zh' ? '全球' : 'Global')
    setErrorMessage(null)
  }

  return {
    title: t('directed.title'),
    eyebrow: t('directed.eyebrow'),
    description: t('directed.description'),
    viewModel,
    isSubmitting,
    setKeywords,
    setSubreddits,
    setRegionHint,
    setSubmissionMode,
    handleSubmit,
    handleUseExample,
  }
}
