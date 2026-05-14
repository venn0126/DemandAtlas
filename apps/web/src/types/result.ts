import type { ApiEnvelope } from './common'

export type BoardType = 'hot' | 'growth' | 'opportunity'

export type ResultSnapshotSummary = {
  result_snapshot_id: string
  query_task_id: string
  query_type: 'one_click' | 'directed'
  view_type: 'active' | 'new'
  time_window: {
    start_at: string
    end_at: string
  }
  generated_at: string
  coverage_note: string | null
  sync_freshness_note: string
  summary_stats: {
    cluster_count: number
    post_count: number
    comment_count: number
  }
  available_boards: BoardType[]
}

export type ResultSnapshotSummaryResponse = ApiEnvelope<ResultSnapshotSummary>

export type BoardEvidenceSnippet = {
  evidence_id: string
  excerpt: string
  subreddit: string
  created_at: string
  availability_status: string
  source_url: string | null
}

export type BoardItem = {
  rank: number
  cluster_id: string
  title: string
  summary: string
  board_score: number
  discussion_score: number
  attention_score: number
  growth_score: number
  opportunity_score: number
  confidence_score: number
  post_count: number
  comment_count: number
  unique_user_count: number
  is_weak_signal: boolean
  is_low_confidence: boolean
  is_emerging_signal: boolean
  top_subreddits: string[]
  highlight_evidence: BoardEvidenceSnippet[]
}

export type BoardResult = {
  board_type: BoardType
  items: BoardItem[]
}

export type BoardResultResponse = ApiEnvelope<
  BoardResult,
  null,
  {
    next_page_token: string | null
  }
>
