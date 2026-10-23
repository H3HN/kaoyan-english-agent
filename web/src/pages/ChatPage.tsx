import { useEffect, useRef, useState } from 'react'
import {
  BookOpen,
  CalendarDays,
  GitBranch,
  Languages,
  RotateCcw,
  Send,
  Sparkles,
  Wrench,
  Target,
} from 'lucide-react'
import { Tag } from '../components/Tag'
import {
  api,
  type ChatWorkflow,
  type Citation,
  type PassageSummary,
  type ToolCall,
} from '../lib/api'
import { useAppStore } from '../store/AppStore'
import { useToast } from '../components/Toast'

interface ChatSection {
  title: string
  body?: string
  items?: string[]
  code?: string
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  intro?: string
  sections?: ChatSection[]
  tools?: ToolCall[]
  citations?: Citation[]
  source?: 'server' | 'local'
  llmUsed?: boolean
}

const initialMessages: ChatMessage[] = [
  {
    id: 'welcome',
    role: 'assistant',
    intro: '把正在读的句子、做错的选项或复习计划发给我。',
  },
]

const presetPrompts = [
  {
    title: '解析这个句子的从句',
    prompt: '请按五步法解析当前上下文中的长难句，标出主干、从句和修饰。',
  },
  {
    title: '提炼本段核心词',
    prompt: '请提炼当前上下文中的核心词，区分大纲词与熟词僻义。',
  },
  {
    title: '分析这道题的错误选项',
    prompt: '请分析当前上下文中第一道题的四个选项，标注陷阱类型。',
  },
  {
    title: '安排本周复习计划',
    prompt: '请根据我的单词本，安排本周的复习计划。',
  },
  {
    title: '总结段落主旨',
    prompt: '请总结这段的主旨和作者态度，并指出主旨题的定位句。',
  },
  {
    title: '查一个熟词僻义',
    prompt: 'address、plant、subject 在考研里有哪些熟词僻义？',
  },
]

function AssistantBubble({ message }: { message: ChatMessage }) {
  return (
    <div className="w-full max-w-4xl">
      <div className="mb-1.5 flex items-center gap-2">
        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-800 text-white">
          <Sparkles className="h-3.5 w-3.5" />
        </span>
        <span className="text-[11px] font-semibold text-slate-700">
          研英 Agent
        </span>
      </div>
      <div className="rounded-2xl rounded-tl-md border border-slate-200 bg-slate-50/80 p-4">
        {message.intro ? (
          <p className="text-[13px] leading-7 text-slate-700">
            {message.intro}
          </p>
        ) : null}

        {message.sections?.length ? (
          <div className="mt-3 grid gap-2 sm:grid-cols-2">
            {message.sections.map((section) => (
              <div
                key={section.title}
                className="rounded-lg border border-slate-200 bg-white p-3"
              >
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
                  {section.title}
                </p>
                {section.body ? (
                  <p className="mt-1.5 text-xs leading-6 text-slate-600">
                    {section.body}
                  </p>
                ) : null}
                {section.items ? (
                  <ul className="mt-2 space-y-1.5">
                    {section.items.map((item) => (
                      <li
                        key={item}
                        className="flex items-start gap-2 text-xs leading-6 text-slate-600"
                      >
                        <span className="mt-2.5 h-1 w-1 shrink-0 rounded-full bg-slate-400" />
                        {item}
                      </li>
                    ))}
                  </ul>
                ) : null}
                {section.code ? (
                  <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-200 bg-slate-50 px-3 py-2.5 font-serif text-[12.5px] leading-6 whitespace-pre-wrap text-slate-700">
                    {section.code}
                  </pre>
                ) : null}
              </div>
            ))}
          </div>
        ) : null}

        {message.tools?.length || message.citations?.length ? (
          <div className="mt-3 rounded-lg border border-slate-200 bg-white px-3 py-2.5">
            <div className="flex items-center gap-1.5">
              <Wrench className="h-2.5 w-2.5 text-slate-400" />
              <span className="text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Tool trace
              </span>
              {message.llmUsed ? (
                <Tag tone="violet" className="ml-auto text-[9px]">
                  DeepSeek 生成
                </Tag>
              ) : message.source === 'local' ? (
                <Tag tone="amber" className="ml-auto text-[9px]">
                  本地兜底
                </Tag>
              ) : null}
            </div>
            {message.tools?.length ? (
              <div className="mt-1.5 flex flex-wrap gap-1.5">
                {message.tools.map((tool, index) => (
                  <span
                    key={`${tool.tool}-${index}`}
                    title={tool.summary}
                    className="inline-flex items-center gap-1 rounded-md bg-slate-50 px-1.5 py-1 text-[9px] font-medium text-slate-500 ring-1 ring-slate-100"
                  >
                    <code className="font-mono text-[9px]">{tool.tool}</code>
                    <span className="text-slate-300">·</span>
                    <span className="max-w-[180px] truncate">{tool.summary}</span>
                  </span>
                ))}
              </div>
            ) : null}
            {message.citations?.length ? (
              <div className="mt-2 flex flex-wrap gap-1.5 border-t border-slate-100 pt-2">
                {message.citations.slice(0, 3).map((citation) => (
                  <Tag key={citation.id} tone="emerald" title={citation.text}>
                    {citation.source}
                  </Tag>
                ))}
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const counter = useRef(0)
  const { connected, refresh } = useAppStore()
  const [contexts, setContexts] = useState<PassageSummary[]>([])
  const [contextId, setContextId] = useState('')
  const context = contexts.find((item) => item.id === contextId) ?? contexts[0]
  const toast = useToast()

  useEffect(() => {
    let alive = true
    api
      .getPassages()
      .then((response) => {
        if (!alive) return
        setContexts(response.items)
        if (response.items[0]) setContextId(response.items[0].id)
      })
      .catch(() => {
        if (alive) toast('无法读取上下文列表，请检查后端服务。', 'error')
      })
    return () => {
      alive = false
    }
  }, [toast])

  useEffect(() => {
    const node = scrollRef.current
    if (node) {
      node.scrollTop = node.scrollHeight
    }
  }, [messages, typing])

  useEffect(() => {
    const node = textareaRef.current
    if (!node) return
    node.style.height = 'auto'
    node.style.height = `${Math.min(node.scrollHeight, 112)}px`
  }, [input])

  const send = async (raw?: string) => {
    const text = (raw ?? input).trim()
    if (!text || typing || !contextId) return

    counter.current += 1
    const userMessage: ChatMessage = {
      id: `u-${counter.current}`,
      role: 'user',
      intro: text,
    }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setTyping(true)

    try {
      const reply: ChatWorkflow = await api.chat(text, contextId)
      counter.current += 1
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${counter.current}`,
          role: 'assistant',
          intro: reply.intro,
          sections: reply.sections,
          tools: reply.tool_trace,
          citations: reply.citations,
          source: 'server',
          llmUsed: reply.llm_used,
        },
      ])
      if (
        reply.tool_trace.some((tool) => tool.tool === 'add_to_vocab_book')
      ) {
        void refresh()
      }
    } catch {
      counter.current += 1
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${counter.current}`,
          role: 'assistant',
          intro:
            '后端未连接，暂时无法调用词库与真题工具。请确认 FastAPI（8000 端口）运行后重试。',
          source: 'local',
        },
      ])
    } finally {
      setTyping(false)
    }
  }

  const clearChat = () => {
    setTyping(false)
    setMessages(initialMessages)
    toast('对话已重置。', 'info')
  }

  return (
    <div className="h-[calc(100dvh-104px)] min-h-[560px] lg:h-[calc(100dvh-64px)]">
      <section className="flex h-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <header className="flex min-h-14 flex-wrap items-center justify-between gap-2 border-b border-slate-200 px-4 py-2 sm:px-5">
          <div className="flex items-center gap-3">
            <span className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-slate-800 text-white">
              <Sparkles className="h-4 w-4" />
              <span
                className={`absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-white ${
                  connected ? 'bg-emerald-400' : 'bg-amber-400'
                }`}
              />
            </span>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-semibold text-slate-900">
                研英 Agent
              </h1>
              <Tag tone={connected ? 'emerald' : 'amber'} dot>
                {connected ? '后端已连接' : '本地示例'}
              </Tag>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="hidden items-center gap-1.5 md:flex">
              <Tag tone="emerald">句子 {context?.sentence_count ?? 0}</Tag>
              <Tag tone="amber">题目 {context?.question_count ?? 0}</Tag>
            </div>
            <select
              value={contextId}
              onChange={(event) => {
                setContextId(event.target.value)
                toast('上下文已切换。', 'info')
              }}
              aria-label="选择上下文"
              className="h-8 max-w-[170px] rounded-lg border border-slate-200 bg-white px-2 text-[11px] font-medium text-slate-600 outline-none"
            >
              {contexts.length === 0 ? (
                <option value="">加载文章…</option>
              ) : null}
              {contexts.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.year} {item.exam_type} · Text {item.text_number}
                </option>
              ))}
            </select>
            <button
              type="button"
              onClick={clearChat}
              className="inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 text-[11px] font-medium text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-800"
            >
              <RotateCcw className="h-3 w-3" />
              清空
            </button>
          </div>
        </header>

        <div
          ref={scrollRef}
          className="scrollbar-thin flex-1 space-y-4 overflow-y-auto p-4 sm:p-6"
        >
          {messages.map((message) =>
            message.role === 'assistant' ? (
              <AssistantBubble key={message.id} message={message} />
            ) : (
              <div key={message.id} className="flex justify-end">
                <div className="max-w-[82%] rounded-2xl rounded-br-md bg-slate-800 px-4 py-3 text-[13px] leading-7 text-white shadow-sm sm:max-w-2xl">
                  {message.intro}
                </div>
              </div>
            ),
          )}

          {typing ? (
            <div className="flex items-center gap-2.5">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-800 text-white">
                <Sparkles className="h-3.5 w-3.5" />
              </span>
              <div className="flex items-center gap-1 rounded-full border border-slate-200 bg-slate-50 px-3 py-2">
                <span className="typing-dot h-1.5 w-1.5 rounded-full bg-slate-400" />
                <span
                  className="typing-dot h-1.5 w-1.5 rounded-full bg-slate-400"
                  style={{ animationDelay: '0.15s' }}
                />
                <span
                  className="typing-dot h-1.5 w-1.5 rounded-full bg-slate-400"
                  style={{ animationDelay: '0.3s' }}
                />
              </div>
            </div>
          ) : null}
        </div>

        <div className="border-t border-slate-200 bg-slate-50/50 p-3 sm:p-4">
          <div className="mb-2 flex gap-1.5 overflow-x-auto pb-1">
            {presetPrompts.map((preset) => (
              <button
                key={preset.title}
                type="button"
                onClick={() => void send(preset.prompt)}
                disabled={typing}
                className="shrink-0 whitespace-nowrap rounded-full border border-slate-200 bg-white px-3 py-1.5 text-[11px] font-medium text-slate-500 transition-colors hover:border-slate-300 hover:text-slate-800 disabled:opacity-50"
              >
                {preset.title}
              </button>
            ))}
          </div>

          <div className="flex items-end gap-2">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  void send()
                }
              }}
              rows={1}
              aria-label="向 Agent 提问"
              placeholder="向 Agent 提问：解析此句从句、提炼核心词、分析选项…"
              className="max-h-28 min-h-[44px] flex-1 resize-none rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm leading-6 text-slate-800 outline-none transition-colors placeholder:text-slate-400 focus:border-slate-300"
            />
            <button
              type="button"
              onClick={() => void send()}
              disabled={!input.trim() || typing}
              aria-label="发送消息"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-slate-800 text-white transition-colors hover:bg-slate-900 disabled:bg-slate-200 disabled:text-slate-400"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
          <p className="mt-1.5 text-[10px] text-slate-400">
            Enter 发送 · Shift + Enter 换行
          </p>
        </div>
      </section>
    </div>
  )
}
