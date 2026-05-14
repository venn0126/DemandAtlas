import type { QueryTaskStatusData, QueryTaskStatus, TopicTemplateListItem } from '../types/query'
import type {
  KeyValueRowViewModel,
  DirectedQueryViewModel,
  OneClickQueryViewModel,
  SelectOptionViewModel,
  TaskStatusViewModel,
} from '../types/view-model'

const taskToneMap: Record<QueryTaskStatus, TaskStatusViewModel['statusTone']> = {
  pending: 'info',
  running: 'info',
  partial_success: 'warning',
  success: 'success',
  failed: 'danger',
}

export function toTemplateSelectOptions(
  items: TopicTemplateListItem[],
): SelectOptionViewModel[] {
  return items.map((item) => ({
    value: item.template_id,
    label: item.name,
  }))
}

export function toTaskStatusViewModel(input: {
  task: QueryTaskStatusData
  taskIdFallback: string
  statusLabel: string
  stageLabel: string
}): TaskStatusViewModel {
  const { stageLabel, statusLabel, task, taskIdFallback } = input

  return {
    taskId: task.query_task_id || taskIdFallback,
    statusLabel,
    stageLabel,
    statusTone: taskToneMap[task.status],
    currentStep: task.progress.current_step,
    totalSteps: task.progress.total_steps,
    progressPercent: task.progress.percent,
  }
}

export function toTaskSummaryRows(rows: KeyValueRowViewModel[]) {
  return rows
}

export function toOneClickQueryViewModel(input: {
  templateBadge: string
  mockBadge: string
  loadingTitle: string
  errorTitle: string
  errorDescription: string
  templates: TopicTemplateListItem[]
  templateLabel: string
  templateValue: string
  timeWindowLabel: string
  timeWindowValue: string
  viewTypeLabel: string
  viewTypeValue: string
  detailBannerTitle?: string
  detailBannerDescription?: string
  submissionModeLabel: string
  submissionModeValue: string
  submissionModeOptions: SelectOptionViewModel[]
  submitLabel: string
  submittingLabel: string
  toggleModeLabel: string
}): OneClickQueryViewModel {
  return {
    templateBadge: input.templateBadge,
    mockBadge: input.mockBadge,
    loadingTitle: input.loadingTitle,
    errorTitle: input.errorTitle,
    errorDescription: input.errorDescription,
    templateOptions: toTemplateSelectOptions(input.templates),
    templateLabel: input.templateLabel,
    templateValue: input.templateValue,
    timeWindowLabel: input.timeWindowLabel,
    timeWindowValue: input.timeWindowValue,
    viewTypeLabel: input.viewTypeLabel,
    viewTypeValue: input.viewTypeValue,
    detailBannerTitle: input.detailBannerTitle,
    detailBannerDescription: input.detailBannerDescription,
    submissionModeLabel: input.submissionModeLabel,
    submissionModeValue: input.submissionModeValue,
    submissionModeOptions: input.submissionModeOptions,
    submitLabel: input.submitLabel,
    submittingLabel: input.submittingLabel,
    toggleModeLabel: input.toggleModeLabel,
  }
}

export function toDirectedQueryViewModel(input: {
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
}): DirectedQueryViewModel {
  return {
    queryBadge: input.queryBadge,
    mockBadge: input.mockBadge,
    keywordsLabel: input.keywordsLabel,
    keywordsValue: input.keywordsValue,
    keywordsHint: input.keywordsHint,
    subredditsLabel: input.subredditsLabel,
    subredditsValue: input.subredditsValue,
    subredditsHint: input.subredditsHint,
    regionLabel: input.regionLabel,
    regionValue: input.regionValue,
    regionHint: input.regionHint,
    languageLabel: input.languageLabel,
    languageValue: input.languageValue,
    timeWindowLabel: input.timeWindowLabel,
    timeWindowValue: input.timeWindowValue,
    engagementLabel: input.engagementLabel,
    engagementValue: input.engagementValue,
    submissionModeLabel: input.submissionModeLabel,
    submissionModeValue: input.submissionModeValue,
    submissionModeOptions: input.submissionModeOptions,
    validationTitle: input.validationTitle,
    errorMessage: input.errorMessage,
    submitLabel: input.submitLabel,
    submittingLabel: input.submittingLabel,
    useExampleLabel: input.useExampleLabel,
  }
}
