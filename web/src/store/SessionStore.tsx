import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import {
  api,
  type AdHocSentenceData,
  type AgentResponse,
  type AgentWidget,
  type ChatSection,
  type Citation,
  type ClientAction,
  type ClientContext,
  type ToolCall,
} from '../lib/api'
import { useWorkspace } from './WorkspaceStore'

export interface AgentMessage {
  id: string
  role: 'user' | 'assistant'
  intro: string
  sections?: ChatSection[]
  tools?: ToolCall[]
  citations?: Citation[]
  widgets?: AgentWidget[]
  actions?: ClientAction[]
  llmUsed?: boolean
  isAuto?: boolean
}

interface SessionValue {
  messages: AgentMessage[]
  typing: boolean
  sendMessage: (text: string) => Promise<void>
  sendAutoEvent: (
    event: NonNullable<ClientContext['recent_event']>,
  ) => Promise<void>
  clearMessages: () => void
}

function contentFromUnit(unit: ReturnType<typeof useWorkspace>['workspaceUnit']) {
  if (!unit) return { type: null, title: null, text: null }
  if (unit.tier === 'reader') {
    const data = unit.data as { title?: string; text?: string }
    return { type: 'reader' as const, title: data.title ?? unit.label, text: data.text ?? null }
  }
  if (unit.tier === 'paragraph') {
    const data = unit.data as { paragraph_en?: string }
    return { type: 'paragraph' as const, title: unit.label, text: data.paragraph_en ?? null }
  }
  if (unit.tier === 'listening') {
    const data = unit.data as { source_label?: string; sentences?: { text: string }[] }
    return {
      type: 'listening' as const,
      title: data.source_label ?? unit.label,
      text: (data.sentences ?? []).map((item) => item.text).join(' ') || null,
    }
  }
  if (unit.tier === 'writing') {
    const data = unit.data as { prompt?: string; draft?: string }
    return { type: 'writing' as const, title: data.prompt ?? unit.label, text: data.draft ?? null }
  }
  return { type: null, title: null, text: null }
}

const SessionContext = createContext<SessionValue | null>(null)

export function SessionProvider({ children }: { children: ReactNode }) {
  const { context, workspaceUnit } = useWorkspace()
  const [messages, setMessages] = useState<AgentMessage[]>([])
  const [typing, setTyping] = useState(false)
  const counter = useRef(0)

  const append = useCallback((message: Omit<AgentMessage, 'id'>) => {
    counter.current += 1
    setMessages((prev) => [
      ...prev.slice(-30),
      { ...message, id: `${message.role}-${counter.current}` },
    ])
  }, [])

  const request = useCallback(
    async (
      text: string,
      triggerMode: 'USER_CHAT' | 'AUTO_EVENT',
      event?: ClientContext['recent_event'],
    ) => {
      const sentenceData =
        workspaceUnit?.tier === 'sentence'
          ? (workspaceUnit.data as AdHocSentenceData)
          : null
      const activeContent =
        context.current_route === '/studio'
          ? contentFromUnit(workspaceUnit)
          : { type: null, title: null, text: null }
      const requestContext: ClientContext = {
        ...context,
        active_sentence_id:
          workspaceUnit?.tier === 'sentence' ? workspaceUnit.id : context.active_sentence_id,
        active_sentence_data: sentenceData,
        active_sentence_source_type:
          workspaceUnit?.tier === 'sentence'
            ? workspaceUnit.saved
              ? 'USER_SAVED'
              : 'AD_HOC_DRAFT'
            : null,
        active_content_type: activeContent.type,
        active_content_title: activeContent.title,
        active_content_text: activeContent.text,
        trigger_mode: triggerMode,
        recent_event: event ?? null,
      }
      setTyping(true)
      try {
        const response: AgentResponse = await api.agentChat(text, requestContext)
        append({
          role: 'assistant',
          intro: response.intro,
          sections: response.sections,
          tools: response.tool_trace,
          citations: response.citations,
          widgets: response.widgets,
          actions: response.client_actions,
          llmUsed: response.llm_used,
          isAuto: triggerMode === 'AUTO_EVENT',
        })
      } catch {
        append({
          role: 'assistant',
          intro: '后端暂时不可用，Agent 无法连接工具与学习数据。请确认 FastAPI 已启动。',
        })
      } finally {
        setTyping(false)
      }
    },
    [append, context, workspaceUnit],
  )

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim()
      if (!trimmed || typing) return
      append({ role: 'user', intro: trimmed })
      await request(trimmed, 'USER_CHAT')
    },
    [append, request, typing],
  )

  const sendAutoEvent = useCallback(
    async (event: NonNullable<ClientContext['recent_event']>) => {
      if (typing) return
      await request('系统自动事件：请根据当前页面上下文主动给出简短诊断。', 'AUTO_EVENT', event)
    },
    [request, typing],
  )

  const clearMessages = useCallback(() => setMessages([]), [])

  const value = useMemo<SessionValue>(
    () => ({ messages, typing, sendMessage, sendAutoEvent, clearMessages }),
    [messages, typing, sendMessage, sendAutoEvent, clearMessages],
  )

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>
}

export function useSession() {
  const value = useContext(SessionContext)
  if (!value) throw new Error('useSession must be used within SessionProvider')
  return value
}
