import type { ApiEnvelope } from './common'

export type EvidenceItem = {
  evidence_id: string
  excerpt: string
  subreddit: string
  created_at: string
  availability_status: string
  source_url: string | null
}

export type DetailScores = {
  discussion_score: number
  attention_score: number
  growth_score: number
  opportunity_score: number
  confidence_score: number
}

export type DetailMetrics = {
  post_count: number
  comment_count: number
  unique_user_count: number
  community_spread_count: number
}

export type ClusterDetail = {
  cluster_id: string
  title: string
  summary: string
  time_window: {
    start_at: string
    end_at: string
  }
  flags: {
    is_weak_signal: boolean
    is_low_confidence: boolean
    is_emerging_signal: boolean
  }
  scores: DetailScores
  metrics: DetailMetrics
  scenes: string[]
  pain_points: string[]
  alternatives: string[]
  supporting_evidence: EvidenceItem[]
  opposing_evidence: EvidenceItem[]
  top_subreddits: string[]
  coverage_note: string | null
}

export type ClusterDetailResponse = ApiEnvelope<
  ClusterDetail,
  null,
  {
    evidence_next_page_token: string | null
  }
>
