import { BookOpenCheck, Quote, Workflow, Wrench } from 'lucide-react'
import type { Citation, ToolCall } from '../lib/api'
import { Tag } from './Tag'

export function ToolTrace({
  tools,
  title = 'Agent 工具链',
  className = '',
}: {
  tools: ToolCall[]
  title?: string
  className?: string
}) {
  if (tools.length === 0) return null
  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white p-4 shadow-sm ${className}`}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-800 text-white">
            <Workflow className="h-3.5 w-3.5" />
          </span>
          <div>
            <h3 className="text-xs font-semibold text-slate-900">{title}</h3>
            <p className="text-[10px] text-slate-400">
              由 FastAPI 工具层执行，结果可追溯
            </p>
          </div>
        </div>
        <Tag tone="emerald" dot>
          {tools.length} 次调用
        </Tag>
      </div>
      <div className="mt-3 space-y-2">
        {tools.map((tool, index) => (
          <div
            key={`${tool.tool}-${index}`}
            className="flex flex-col gap-1 rounded-lg border border-slate-100 bg-slate-50/70 px-3 py-2 sm:flex-row sm:items-center sm:justify-between"
          >
            <div className="flex min-w-0 items-start gap-2">
              <Wrench className="mt-0.5 h-3 w-3 shrink-0 text-slate-400" />
              <div className="min-w-0">
                <code className="font-mono text-[10px] font-semibold text-slate-600">
                  {tool.tool}
                </code>
                <p className="mt-0.5 text-[11px] leading-relaxed text-slate-500">
                  {tool.summary}
                </p>
              </div>
            </div>
            <span className="shrink-0 pl-5 text-[10px] text-slate-400 tabular-nums sm:pl-0">
              {tool.duration_ms}ms
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function CitationList({
  citations,
  compact = false,
}: {
  citations: Citation[]
  compact?: boolean
}) {
  if (citations.length === 0) return null
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center gap-2">
        <BookOpenCheck className="h-3.5 w-3.5 text-emerald-500" />
        <h3 className="text-xs font-semibold text-slate-900">真题溯源</h3>
        <span className="text-[10px] text-slate-400">
          强制标注出处
        </span>
      </div>
      <div className={`mt-3 space-y-2.5 ${compact ? '' : 'max-h-[320px] overflow-y-auto scrollbar-thin'}`}>
        {citations.map((citation) => (
          <div
            key={citation.id}
            className="rounded-lg border border-slate-100 bg-slate-50/60 px-3 py-2.5"
          >
            <div className="flex flex-wrap items-center gap-1.5">
              <Tag tone="emerald">{citation.source}</Tag>
              {citation.grammar_tags.slice(0, 2).map((tag) => (
                <Tag key={tag} tone="slate">
                  {tag}
                </Tag>
              ))}
            </div>
            <p className="mt-1.5 flex gap-1.5 text-[11px] leading-relaxed text-slate-600">
              <Quote className="mt-0.5 h-3 w-3 shrink-0 text-slate-300" />
              {citation.text}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
