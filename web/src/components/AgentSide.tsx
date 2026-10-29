import { useEffect, useRef } from 'react'
import { Sparkles } from 'lucide-react'
import { useSession, type AgentMessage } from '../store/SessionStore'
import { useWorkspace } from '../store/WorkspaceStore'
import { useAgentActions } from '../lib/useAgentActions'
import { AgentWidgetView } from './AgentWidgets'
import { OmniComposer, type QuickPill } from './OmniComposer'
import { Tag } from './Tag'

const PILLS: Record<string, QuickPill[]> = {
  '/reading': [
    { label: '📒 把本篇生词去重入库', prompt: '把这篇阅读里的生词整理入库。' },
    { label: '🔍 深度剖析本题四个选项', prompt: '请分析当前这道题的选项和陷阱。' },
    { label: '🧬 五步拆解当前定位句', prompt: '请拆解当前定位句的从句。' },
  ],
  '/studio': [
    { label: '🧬 五步拆解当前句', prompt: '请用五步法拆解当前句子。' },
    { label: '📒 提取本段核心词', prompt: '把这段里的生词整理入库。' },
    { label: '🔍 解析当前词', prompt: '请解析当前选中的单词。' },
  ],
  '/vocab': [
    { label: '🃏 抽查到期生词', prompt: '帮我抽查今天到期的单词。' },
    { label: '📅 按错题排计划', prompt: '根据我最近的错题安排三天学习计划。' },
  ],
  '/dashboard': [
    { label: '🚀 今天读哪篇？', prompt: '今天读什么？请直接给我文章并带我去。' },
    { label: '🃏 抽查到期生词', prompt: '帮我抽查今天到期的单词。' },
    { label: '📅 按近期错题排计划', prompt: '根据我最近的错题安排三天学习计划。' },
  ],
}

function CompactTrace({ message }: { message: AgentMessage }) {
  const tools = message.tools ?? []
  const citations = message.citations ?? []
  if (!tools.length && !citations.length) return null
  return (
    <details className="group mt-2 rounded-lg border border-slate-100 bg-white/70 px-2 py-1.5">
      <summary className="cursor-pointer list-none text-[10px] text-slate-400 hover:text-slate-600">
        ⚡ 已检索 {tools.length} 个工具
        {citations.length ? ` · ${citations.length} 条真题溯源` : ''}
      </summary>
      <div className="mt-1.5 space-y-1 border-t border-slate-100 pt-1.5">
        {tools.map((tool, index) => (
          <p key={`${tool.tool}-${index}`} className="text-[9px] leading-4 text-slate-400">
            {tool.tool} · {tool.summary} · {tool.duration_ms}ms
          </p>
        ))}
        {citations.map((citation) => (
          <p key={citation.id} className="text-[9px] leading-4 text-emerald-700">
            {citation.source} · {citation.text.slice(0, 90)}
          </p>
        ))}
      </div>
    </details>
  )
}

function Message({ message, onAction }: { message: AgentMessage; onAction: (action: import('../lib/api').ClientAction) => void }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[92%] rounded-2xl rounded-br-md bg-slate-900 px-4 py-3 text-[15px] leading-7 text-white">
          {message.intro}
        </div>
      </div>
    )
  }
  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-1.5">
        <span className="flex h-5 w-5 items-center justify-center rounded-md bg-slate-900 text-white">
          <Sparkles className="h-2.5 w-2.5" />
        </span>
        <span className="text-[9px] font-semibold text-slate-500">Agent</span>
        {message.isAuto ? <Tag tone="violet">AUTO</Tag> : null}
        {message.llmUsed ? <Tag tone="violet">DeepSeek</Tag> : null}
      </div>
      <div className="rounded-xl border border-slate-200 bg-slate-50/60 p-4">
        <p className="text-[15px] leading-7 text-slate-800">{message.intro}</p>
        {message.sections?.length ? (
          <div className="mt-3 space-y-3">
            {message.sections.map((section) => (
              <div key={section.title} className="rounded-lg border border-slate-200 bg-white p-3">
                <p className="text-sm font-semibold text-slate-900">
                  {section.title}
                </p>
                {section.body ? (
                  <p className="mt-1 text-[14.5px] leading-relaxed text-slate-600">{section.body}</p>
                ) : null}
                {section.items?.length ? (
                  <ul className="mt-2 space-y-2">
                    {section.items.map((item) => (
                      <li key={item} className="flex items-start gap-2 text-[14.5px] leading-relaxed text-slate-600">
                        <span className="mt-2.5 h-1 w-1 shrink-0 rounded-full bg-slate-400" />
                        {item}
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            ))}
          </div>
        ) : null}
        {message.widgets?.length ? (
          <div className="mt-2 space-y-2">
            {message.widgets.map((widget, index) => (
              <AgentWidgetView key={`${widget.widget_type}-${index}`} widget={widget} onAction={onAction} />
            ))}
          </div>
        ) : null}
        <CompactTrace message={message} />
      </div>
    </div>
  )
}

export function AgentSide() {
  const { currentRoute, workspaceUnit } = useWorkspace()
  const { messages, typing } = useSession()
  const runAction = useAgentActions()
  const scrollRef = useRef<HTMLDivElement>(null)

  const contextualPills =
    workspaceUnit?.tier === 'reader'
      ? [
          { label: '📝 概括主旨', prompt: '概括一下这篇文章的主旨大意。' },
          { label: '🧱 文章结构', prompt: '梳理一下这篇文章的结构。' },
          { label: '📒 提炼生词', prompt: '把这篇里的生词整理入库。' },
        ]
      : workspaceUnit?.tier === 'paragraph'
        ? [
            { label: '📝 概括本段', prompt: '概括一下这一段的主旨。' },
            { label: '🧱 段落逻辑', prompt: '分析这一段的段内逻辑。' },
            { label: '📒 提取本段词', prompt: '把这段里的生词整理入库。' },
          ]
        : workspaceUnit?.tier === 'listening'
          ? [
              { label: '📝 概括听力', prompt: '概括一下这段听力的内容。' },
              { label: '🔁 复述提示', prompt: '给我这段听力的复述框架。' },
            ]
          : null

  useEffect(() => {
    const node = scrollRef.current
    if (node) node.scrollTop = node.scrollHeight
  }, [messages, typing])

  return (
    <aside className="flex h-[42%] min-h-0 w-full shrink-0 flex-col border-t border-slate-200 bg-white lg:h-full lg:w-[440px] lg:shrink-0 lg:border-l lg:border-t-0 xl:w-[480px]">
      <div ref={scrollRef} className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-200 p-4">
            <p className="text-[15px] font-medium text-slate-700">我在看你的画布。</p>
            <p className="mt-2 text-[13.5px] leading-6 text-slate-400">
              选中句子、提交答案或切换文章，我会把定位、陷阱和下一步直接推到画布上。
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <Message key={message.id} message={message} onAction={runAction} />
          ))
        )}
        {typing ? (
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-slate-400" />
            正在读取画布上下文…
          </div>
        ) : null}
      </div>

      <div className="border-t border-slate-100 p-3">
        <OmniComposer pills={contextualPills ?? PILLS[currentRoute] ?? PILLS['/dashboard']} />
      </div>
    </aside>
  )
}
