import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { useLocation } from 'react-router-dom'
import type { AgentRoute, ClientContext, WorkspaceUnit } from '../lib/api'

const WORKSPACE_KEY = 'yanyu.workspace.v1'

function loadWorkspace(): WorkspaceUnit[] {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.sessionStorage.getItem(WORKSPACE_KEY)
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function routeFromPath(pathname: string): AgentRoute {
  if (pathname.startsWith('/studio')) return '/studio'
  if (pathname.startsWith('/reading')) return '/reading'
  if (pathname.startsWith('/vocab')) return '/vocab'
  return '/dashboard'
}

function emptyContext(route: AgentRoute): ClientContext {
  return {
    current_route: route,
    active_passage_id: null,
    active_passage_label: null,
    active_question_id: null,
    active_sentence_id: null,
    selected_raw_text: null,
    active_content_type: null,
    active_content_title: null,
    active_content_text: null,
    trigger_mode: 'USER_CHAT',
    recent_event: null,
  }
}

interface WorkspaceValue {
  currentRoute: AgentRoute
  context: ClientContext
  updateContext: (patch: Partial<ClientContext>) => void
  workspaceUnit: WorkspaceUnit | null
  workspaceStack: WorkspaceUnit[]
  openWorkspaceUnit: (unit: WorkspaceUnit, op?: 'replace' | 'push') => void
  updateWorkspaceUnit: (patch: Partial<WorkspaceUnit>) => void
  popWorkspaceTo: (index: number) => void
  clearWorkspace: () => void
  canvasOp: 'replace' | 'push'
  setCanvasOp: (op: 'replace' | 'push') => void
}

const WorkspaceContext = createContext<WorkspaceValue | null>(null)

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { pathname } = useLocation()
  const currentRoute = routeFromPath(pathname)
  const [context, setContext] = useState<ClientContext>(() => emptyContext(currentRoute))
  const [workspaceStack, setWorkspaceStack] = useState<WorkspaceUnit[]>(loadWorkspace)
  const [canvasOp, setCanvasOp] = useState<'replace' | 'push'>('replace')
  const workspaceUnit = workspaceStack[workspaceStack.length - 1] ?? null

  useEffect(() => {
    setContext((prev) =>
      prev.current_route === currentRoute
        ? prev
        : {
            ...prev,
            current_route: currentRoute,
            active_question_id: null,
            selected_raw_text: null,
            recent_event: null,
          },
    )
  }, [currentRoute])

  const persist = useCallback((units: WorkspaceUnit[]) => {
    setWorkspaceStack(units)
    try {
      window.sessionStorage.setItem(WORKSPACE_KEY, JSON.stringify(units))
    } catch {
      // keep in-memory workspace
    }
  }, [])

  const openWorkspaceUnit = useCallback(
    (unit: WorkspaceUnit, op: 'replace' | 'push' = 'replace') => {
      setWorkspaceStack((prev) => {
        const next = op === 'push' ? [...prev, unit] : [unit]
        try {
          window.sessionStorage.setItem(WORKSPACE_KEY, JSON.stringify(next))
        } catch {
          // ignore
        }
        return next
      })
    },
    [],
  )

  const updateWorkspaceUnit = useCallback((patch: Partial<WorkspaceUnit>) => {
    setWorkspaceStack((prev) => {
      if (!prev.length) return prev
      const next = [...prev]
      next[next.length - 1] = { ...next[next.length - 1], ...patch }
      try {
        window.sessionStorage.setItem(WORKSPACE_KEY, JSON.stringify(next))
      } catch {
        // ignore
      }
      return next
    })
  }, [])

  const popWorkspaceTo = useCallback((index: number) => {
    setWorkspaceStack((prev) => {
      const next = prev.slice(0, index + 1)
      try {
        window.sessionStorage.setItem(WORKSPACE_KEY, JSON.stringify(next))
      } catch {
        // ignore
      }
      return next
    })
  }, [])

  const clearWorkspace = useCallback(() => persist([]), [persist])
  const updateContext = useCallback((patch: Partial<ClientContext>) => {
    setContext((prev) => ({ ...prev, ...patch }))
  }, [])

  const value = useMemo<WorkspaceValue>(
    () => ({
      currentRoute,
      context,
      updateContext,
      workspaceUnit,
      workspaceStack,
      openWorkspaceUnit,
      updateWorkspaceUnit,
      popWorkspaceTo,
      clearWorkspace,
      canvasOp,
      setCanvasOp,
    }),
    [
      currentRoute,
      context,
      updateContext,
      workspaceUnit,
      workspaceStack,
      openWorkspaceUnit,
      updateWorkspaceUnit,
      popWorkspaceTo,
      clearWorkspace,
      canvasOp,
    ],
  )

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>
}

export function useWorkspace() {
  const value = useContext(WorkspaceContext)
  if (!value) throw new Error('useWorkspace must be used within WorkspaceProvider')
  return value
}
