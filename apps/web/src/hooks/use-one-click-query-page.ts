import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, useSearchParams } from 'react-router-dom'

import { toOneClickQueryViewModel } from '../adapters/query'
import { routeBuilders } from '../app/routes'
import { useI18n } from '../i18n/use-i18n'
import { saveAnonymousQuerySession } from '../lib/anonymous-query-session'
import { queryKeys } from '../lib/query-keys'
import { createQueryTask, getTopicTemplateDetail, listTopicTemplates } from '../services/mock-api'
import type { SelectMode } from '../types/common'

export function useOneClickQueryPage() {
  const { t, tDynamic } = useI18n()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [templateId, setTemplateId] = useState(searchParams.get('templateId') ?? 'tpl_ai_tools')
  const [submitMode, setSubmitMode] = useState<Extract<SelectMode, 'async' | 'cache-hit'>>('async')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const templateListQuery = useQuery({
    queryKey: queryKeys.topicTemplates,
    queryFn: listTopicTemplates,
  })

  const templateDetailQuery = useQuery({
    queryKey: queryKeys.topicTemplateDetail(templateId),
    queryFn: getTopicTemplateDetail,
  })

  const viewModel = toOneClickQueryViewModel({
    templateBadge: t('oneClick.badge.template'),
    mockBadge: t('oneClick.badge.mock'),
    loadingTitle: t('oneClick.loadingTemplates'),
    errorTitle: t('oneClick.errorTemplatesTitle'),
    errorDescription: t('oneClick.errorTemplatesDescription'),
    templates: templateListQuery.data?.data.items ?? [],
    templateLabel: t('oneClick.form.template'),
    templateValue: templateId,
    timeWindowLabel: t('oneClick.form.timeWindow'),
    timeWindowValue: t('common.value.last30Days'),
    viewTypeLabel: t('oneClick.form.viewType'),
    viewTypeValue: tDynamic('enum.viewType', 'active'),
    detailBannerTitle: templateDetailQuery.data?.data?.name,
    detailBannerDescription: templateDetailQuery.data?.data
      ? t('oneClick.banner.summary', {
          description: templateDetailQuery.data.data.description,
          count: templateDetailQuery.data.data.candidate_subreddit_count,
        })
      : undefined,
    submissionModeLabel: t('oneClick.form.submissionMode'),
    submissionModeValue: submitMode,
    submissionModeOptions: [
      { value: 'async', label: tDynamic('enum.submissionMode', 'async') },
      { value: 'cache-hit', label: tDynamic('enum.submissionMode', 'cache-hit') },
    ],
    submitLabel: t('oneClick.actions.run'),
    submittingLabel: t('oneClick.actions.submitting'),
    toggleModeLabel: t('oneClick.actions.toggleMode'),
  })

  async function handleSubmit() {
    setIsSubmitting(true)

    try {
      const response = await createQueryTask(submitMode)
      const payload = response.data

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

  return {
    title: t('oneClick.title'),
    eyebrow: t('oneClick.eyebrow'),
    description: t('oneClick.description'),
    viewModel,
    isLoading: templateListQuery.isLoading,
    isError: templateListQuery.isError,
    isSubmitting,
    setTemplateId,
    setSubmitMode,
    handleSubmit,
  }
}
