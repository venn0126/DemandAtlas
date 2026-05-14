export const routes = {
  home: '/',
  oneClick: '/discover/one-click',
  directed: '/discover/directed',
  settings: '/settings',
  task: '/tasks/:queryTaskId',
  result: '/results/:resultSnapshotId',
  resultBoard: '/results/:resultSnapshotId/boards/:boardType',
  clusterDetail: '/results/:resultSnapshotId/clusters/:clusterId',
} as const

export const routeBuilders = {
  task: (queryTaskId: string) => `/tasks/${queryTaskId}`,
  result: (resultSnapshotId: string) => `/results/${resultSnapshotId}`,
  resultBoard: (resultSnapshotId: string, boardType: string) =>
    `/results/${resultSnapshotId}/boards/${boardType}`,
  clusterDetail: (resultSnapshotId: string, clusterId: string) =>
    `/results/${resultSnapshotId}/clusters/${clusterId}`,
  oneClickWithTemplate: (templateId: string) =>
    `/discover/one-click?templateId=${encodeURIComponent(templateId)}`,
} as const
