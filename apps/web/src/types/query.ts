import type { ApiEnvelope } from './common'

export type QueryTaskStatus =
  | 'pending'
  | 'running'
  | 'partial_success'
  | 'success'
  | 'failed'

export type QueryTaskStage =
  | 'validate'
  | 'plan'
  | 'fetch'
  | 'normalize'
  | 'retrieve'
  | 'cluster'
  | 'score'
  | 'snapshot'
  | null

export type TopicTemplateListItem = {
  template_id: string
  template_version_id: string
  name: string
  description: string
  default_language: string
  default_view_type: string
}

export type TopicTemplateListResponse = ApiEnvelope<{
  items: TopicTemplateListItem[]
}>

export type TopicTemplateDetail = {
  template_id: string
  template_version_id: string
  name: string
  description: string
  default_language: string
  default_view_type: string
  candidate_subreddit_count: number
}

export type TopicTemplateDetailResponse = ApiEnvelope<TopicTemplateDetail>

export type QueryTaskCreateAsyncData = {
  execution_mode: 'async'
  query_task_id: string
  status: 'pending'
  poll_url: string
  anonymous_query_access_token: string
}

export type QueryTaskCreateCacheHitData = {
  execution_mode: 'cache_hit'
  query_task_id: string
  status: 'success'
  result_snapshot_id: string
  cached: boolean
}

export type QueryTaskCreateValidationError = {
  code: 'QUERY_TOO_BROAD'
  message: string
  details: {
    max_keywords: number
    max_subreddits: number
  }
}

export type QueryTaskCreateAsyncResponse = ApiEnvelope<
  QueryTaskCreateAsyncData,
  null,
  { retry_after_ms: number }
>

export type QueryTaskCreateCacheHitResponse = ApiEnvelope<QueryTaskCreateCacheHitData>

export type QueryTaskCreateTooBroadResponse = ApiEnvelope<
  null,
  QueryTaskCreateValidationError,
  Record<string, never>
>

export type QueryTaskCreateResponse =
  | QueryTaskCreateAsyncResponse
  | QueryTaskCreateCacheHitResponse
  | QueryTaskCreateTooBroadResponse

export type QueryTaskWarning = {
  code: string
  message: string
}

export type QueryTaskStatusData = {
  query_task_id: string
  status: QueryTaskStatus
  current_stage: QueryTaskStage
  progress: {
    current_step: number
    total_steps: number
    percent: number
  }
  result_snapshot_id: string | null
  coverage_note: string | null
  warnings: QueryTaskWarning[]
}

export type QueryTaskStatusError = {
  code: string
  message: string
  details?: Record<string, unknown>
} | null

export type QueryTaskStatusResponse = ApiEnvelope<QueryTaskStatusData, QueryTaskStatusError>
