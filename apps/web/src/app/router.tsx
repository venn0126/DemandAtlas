import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { AppShell } from '../components/layout/app-shell'
import { HomePage } from '../pages/home-page'
import { OneClickDiscoverPage } from '../pages/one-click-discover-page'
import { DirectedDiscoverPage } from '../pages/directed-discover-page'
import { TaskPage } from '../pages/task-page'
import { ResultPage } from '../pages/result-page'
import { ClusterDetailPage } from '../pages/cluster-detail-page'
import { SettingsPage } from '../pages/settings-page'

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/discover/one-click" element={<OneClickDiscoverPage />} />
          <Route path="/discover/directed" element={<DirectedDiscoverPage />} />
          <Route path="/tasks/:queryTaskId" element={<TaskPage />} />
          <Route path="/results/:resultSnapshotId" element={<ResultPage />} />
          <Route
            path="/results/:resultSnapshotId/boards/:boardType"
            element={<ResultPage />}
          />
          <Route
            path="/results/:resultSnapshotId/clusters/:clusterId"
            element={<ClusterDetailPage />}
          />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
