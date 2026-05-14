import { mockData } from '../lib/mock-data'
import type {
  QueryTaskCreateResponse,
  QueryTaskStatus,
  QueryTaskStatusResponse,
  TopicTemplateDetailResponse,
  TopicTemplateListResponse,
} from '../types/query'
import type { ClusterDetailResponse } from '../types/detail'
import type { BoardResultResponse, BoardType, ResultSnapshotSummaryResponse } from '../types/result'

function sleep(ms: number) {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

export async function listTopicTemplates(): Promise<TopicTemplateListResponse> {
  await sleep(150)
  return mockData.topicTemplatesList as TopicTemplateListResponse
}

export async function getTopicTemplateDetail(): Promise<TopicTemplateDetailResponse> {
  await sleep(120)
  return mockData.topicTemplateDetail as TopicTemplateDetailResponse
}

export async function createQueryTask(
  mode: 'async' | 'cache-hit' | 'too-broad' = 'async',
): Promise<QueryTaskCreateResponse> {
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
    ? (mockData.queryTaskCreateCacheHit as QueryTaskCreateResponse)
    : (mockData.queryTaskCreateAsync as QueryTaskCreateResponse)
}

export async function getQueryTaskStatus(
  status: QueryTaskStatus = 'running',
): Promise<QueryTaskStatusResponse> {
  await sleep(180)

  const statusMap = {
    pending: mockData.queryTaskStatusPending,
    running: mockData.queryTaskStatusRunning,
    partial_success: mockData.queryTaskStatusPartialSuccess,
    success: mockData.queryTaskStatusSuccess,
    failed: mockData.queryTaskStatusFailed,
  }

  return statusMap[status] as QueryTaskStatusResponse
}

export async function getResultSnapshotSummary(
  mode: 'normal' | 'empty' | 'partial' = 'normal',
): Promise<ResultSnapshotSummaryResponse> {
  await sleep(180)

  const summaryMap = {
    normal: mockData.resultSnapshotSummaryNormal,
    empty: mockData.resultSnapshotSummaryEmpty,
    partial: mockData.resultSnapshotSummaryPartial,
  }

  return summaryMap[mode] as ResultSnapshotSummaryResponse
}

export async function getBoardResult(
  boardType: BoardType | 'empty' = 'hot',
): Promise<BoardResultResponse> {
  await sleep(180)

  const boardMap = {
    hot: mockData.resultSnapshotBoardHot,
    growth: mockData.resultSnapshotBoardGrowth,
    opportunity: mockData.resultSnapshotBoardOpportunity,
    empty: mockData.resultSnapshotBoardEmpty,
  }

  return boardMap[boardType] as BoardResultResponse
}

export async function getClusterDetail(
  mode: 'normal' | 'partial' = 'normal',
): Promise<ClusterDetailResponse> {
  await sleep(180)
  return mode === 'partial'
    ? (mockData.clusterDetailPartialEvidence as ClusterDetailResponse)
    : (mockData.clusterDetailNormal as ClusterDetailResponse)
}
