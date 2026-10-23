import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ToastProvider } from './components/Toast'
import { AppStoreProvider } from './store/AppStore'
import ChatPage from './pages/ChatPage'
import ComparisonPage from './pages/ComparisonPage'
import DashboardPage from './pages/DashboardPage'
import KnowledgePage from './pages/KnowledgePage'
import OptionsPage from './pages/OptionsPage'
import ReportPage from './pages/ReportPage'
import SentencePage from './pages/SentencePage'
import WordbookPage from './pages/WordbookPage'

export default function App() {
  return (
    <ToastProvider>
      <AppStoreProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/sentence" element={<SentencePage />} />
            <Route path="/options" element={<OptionsPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/wordbook" element={<WordbookPage />} />
            <Route path="/report" element={<ReportPage />} />
            <Route path="/comparison" element={<ComparisonPage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </AppStoreProvider>
    </ToastProvider>
  )
}
