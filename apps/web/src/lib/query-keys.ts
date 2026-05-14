export const queryKeys = {
  topicTemplates: ['topic-templates'] as const,
  topicTemplateDetail: (templateId: string) => ['topic-template-detail', templateId] as const,
  resultPreview: ['result-preview'] as const,
}
