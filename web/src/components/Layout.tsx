import { useEffect } from 'react'
import type { ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { AgentActionController } from './AgentActionController'
import { AgentSide } from './AgentSide'
import { FlashcardDrawer } from './FlashcardDrawer'
import { OSTopbar } from './OSChrome'
import { useSession } from '../store/SessionStore'

export function Layout({ children }: { children: ReactNode }) {
  const { pathname } = useLocation()
  const { messages } = useSession()
  const zeroState =
    (pathname === '/dashboard' || pathname === '/') && messages.length === 0

  useEffect(() => {
    document.title = '研英 Agent-OS'
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [pathname])

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#F4F6F9]">
      <div className="flex min-w-0 flex-1 flex-col">
        <OSTopbar />
        <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
          <main className="min-h-0 flex-1 overflow-y-auto px-3 py-3 sm:px-4 sm:py-4">
            <div className="mx-auto h-full w-full max-w-[1380px]">{children}</div>
          </main>
          {!zeroState ? <AgentSide /> : null}
        </div>
      </div>
      <AgentActionController />
      <FlashcardDrawer />
    </div>
  )
}
