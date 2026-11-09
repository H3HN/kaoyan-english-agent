import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ToastProvider } from './components/Toast'
import { AppStoreProvider } from './store/AppStore'
import AdminLayout from './admin/AdminLayout'
import AdminKnowledgePage from './admin/KnowledgePage'
import MonitorPage from './admin/MonitorPage'
import WorkbenchPage from './admin/WorkbenchPage'
import ChatPage from './pages/ChatPage'
import DashboardPage from './pages/DashboardPage'
import KnowledgePage from './pages/KnowledgePage'
import LibraryPage from './pages/LibraryPage'
import OptionsPage from './pages/OptionsPage'
import PlanPage from './pages/PlanPage'
import ReportPage from './pages/ReportPage'
import SentencePage from './pages/SentencePage'
import WordbookPage from './pages/WordbookPage'

function StudentShell() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/sentence" element={<SentencePage />} />
        <Route path="/options" element={<OptionsPage />} />
        <Route path="/library" element={<LibraryPage />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/plan" element={<PlanPage />} />
        <Route path="/wordbook" element={<WordbookPage />} />
        <Route path="/report" element={<ReportPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

export default function App() {
  return (
    <ToastProvider>
      <AppStoreProvider>
        <Routes>
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<Navigate to="workbench" replace />} />
            <Route path="workbench" element={<WorkbenchPage />} />
            <Route
              path="knowledge"
              element={<AdminKnowledgePage />}
            />
            <Route
              path="monitor"
              element={<MonitorPage />}
            />
            <Route path="*" element={<Navigate to="workbench" replace />} />
          </Route>
          <Route path="/*" element={<StudentShell />} />
        </Routes>
      </AppStoreProvider>
    </ToastProvider>
  )
}