export type SelectOptionViewModel = {
  value: string
  label: string
}

export type KeyValueRowViewModel = {
  label: string
  value: string
}

export type MetricViewModel = {
  label: string
  value: string | number
}

export type ScoreViewModel = {
  label: string
  value: number
}

export type TaskStatusViewModel = {
  taskId: string
  statusLabel: string
  stageLabel: string
  statusTone: 'info' | 'success' | 'warning' | 'danger'
  currentStep: number
  totalSteps: number
  progressPercent: number
}

export type ResultBoardItemViewModel = {
  clusterId: string
  rank: number
  title: string
  summary: string
  boardScore: number
  topSubreddits: string[]
  isEmergingSignal: boolean
  isLowConfidence: boolean
  isWeakSignal: boolean
}

export type OneClickQueryViewModel = {
  templateBadge: string
  mockBadge: string
  loadingTitle: string
  errorTitle: string
  errorDescription: string
  templateOptions: SelectOptionViewModel[]
  templateLabel: string
  templateValue: string
  timeWindowLabel: string
  timeWindowValue: string
  viewTypeLabel: string
  viewTypeValue: string
  detailBannerTitle?: string
  detailBannerDescription?: string
  submissionModeLabel: string
  submissionModeOptions: SelectOptionViewModel[]
  submissionModeValue: string
  submitLabel: string
  submittingLabel: string
  toggleModeLabel: string
}

export type DirectedQueryViewModel = {
  queryBadge: string
  mockBadge: string
  keywordsLabel: string
  keywordsValue: string
  keywordsHint: string
  subredditsLabel: string
  subredditsValue: string
  subredditsHint: string
  regionLabel: string
  regionValue: string
  regionHint: string
  languageLabel: string
  languageValue: string
  timeWindowLabel: string
  timeWindowValue: string
  engagementLabel: string
  engagementValue: string
  submissionModeLabel: string
  submissionModeValue: string
  submissionModeOptions: SelectOptionViewModel[]
  validationTitle: string
  errorMessage: string | null
  submitLabel: string
  submittingLabel: string
  useExampleLabel: string
}
