import { Navigate, Route, Routes, useSearchParams } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ToastProvider } from './components/Toast'
import { AppStoreProvider } from './store/AppStore'
import { SessionProvider } from './store/SessionStore'
import { UIProvider } from './store/UIStore'
import { WorkspaceProvider } from './store/WorkspaceStore'
import DashboardPage from './pages/DashboardPage'
import OptionsPage from './pages/OptionsPage'
import ReadingHome from './pages/ReadingHome'
import StudioPage from './pages/StudioPage'
import WordbookPage from './pages/WordbookPage'

function ReadingEntry() {
  const [params] = useSearchParams()
  const bounded = params.get('year') || params.get('text') || params.get('exam') || params.get('question_id')
  return bounded ? <OptionsPage /> : <ReadingHome />
}

export default function App() {
  return (
    <ToastProvider>
      <AppStoreProvider>
        <WorkspaceProvider>
          <SessionProvider>
            <UIProvider>
              <Layout>
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/studio" element={<StudioPage />} />
              <Route path="/reading" element={<ReadingEntry />} />
              <Route path="/vocab" element={<WordbookPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
              </Layout>
            </UIProvider>
          </SessionProvider>
        </WorkspaceProvider>
      </AppStoreProvider>
    </ToastProvider>
  )
}
