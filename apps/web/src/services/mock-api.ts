import { mockData } from '../lib/mock-data'

function sleep(ms: number) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

type TopicTemplateListResponse = typeof mockData.topicTemplatesList
type TopicTemplateDetailResponse = typeof mockData.topicTemplateDetail
type QueryTaskCreateAsyncResponse = typeof mockData.queryTaskCreateAsync
type QueryTaskCreateCacheHitResponse = typeof mockData.queryTaskCreateCacheHit
type QueryTaskCreateTooBroadResponse = {
  request_id: string
  data: null
  meta: Record<string, never>
  error: {
    code: string
    message: string
    details: {
      max_keywords: number
      max_subreddits: number
    }
  }
}

export async function listTopicTemplates(): Promise<TopicTemplateListResponse> {
  await sleep(150)
  return mockData.topicTemplatesList
}

export async function getTopicTemplateDetail(): Promise<TopicTemplateDetailResponse> {
  await sleep(120)
  return mockData.topicTemplateDetail
}

export async function createQueryTask(
  mode: 'async' | 'cache-hit' | 'too-broad' = 'async',
): Promise<
  QueryTaskCreateAsyncResponse | QueryTaskCreateCacheHitResponse | QueryTaskCreateTooBroadResponse
> {
  await sleep(250)

  if (mode === 'too-broad') {
    return {
      request_id: 'req_qt_create_422_001',
      data: null,
      meta: {},
      error: {
        code: 'QUERY_TOO_BROAD',
        message: 'query scope is too broad for V1 execution limits',
        details: {
          max_keywords: 5,
          max_subreddits: 20,
        },
      },
    }
  }

  return mode === 'cache-hit'
    ? mockData.queryTaskCreateCacheHit
    : mockData.queryTaskCreateAsync
}

export async function getQueryTaskStatus(
  status: 'pending' | 'running' | 'partial_success' | 'success' | 'failed' = 'running',
) {
  await sleep(180)

  const statusMap = {
    pending: mockData.queryTaskStatusPending,
    running: mockData.queryTaskStatusRunning,
    partial_success: mockData.queryTaskStatusPartialSuccess,
    success: mockData.queryTaskStatusSuccess,
    failed: mockData.queryTaskStatusFailed,
  }

  return statusMap[status]
}

export async function getResultSnapshotSummary(
  mode: 'normal' | 'empty' | 'partial' = 'normal',
) {
  await sleep(180)

  const summaryMap = {
    normal: mockData.resultSnapshotSummaryNormal,
    empty: mockData.resultSnapshotSummaryEmpty,
    partial: mockData.resultSnapshotSummaryPartial,
  }

  return summaryMap[mode]
}

export async function getBoardResult(
  boardType: 'hot' | 'growth' | 'opportunity' | 'empty' = 'hot',
) {
  await sleep(180)

  const boardMap = {
    hot: mockData.resultSnapshotBoardHot,
    growth: mockData.resultSnapshotBoardGrowth,
    opportunity: mockData.resultSnapshotBoardOpportunity,
    empty: mockData.resultSnapshotBoardEmpty,
  }

  return boardMap[boardType]
}

export async function getClusterDetail(mode: 'normal' | 'partial' = 'normal') {
  await sleep(180)
  return mode === 'partial'
    ? mockData.clusterDetailPartialEvidence
    : mockData.clusterDetailNormal
}
