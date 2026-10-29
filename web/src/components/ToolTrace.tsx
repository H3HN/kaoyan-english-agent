import { BookOpenCheck, Quote, Wrench } from 'lucide-react'
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
    <details
      className={`group rounded-lg border border-slate-100 bg-white/60 px-2.5 py-1.5 ${className}`}
    >
      <summary className="cursor-pointer list-none text-[10px] text-slate-400 hover:text-slate-600">
        ⚡ {title} · {tools.length} 次调用
        <span className="ml-1 text-slate-300">（悬停或点击展开）</span>
      </summary>
      <div className="mt-1.5 space-y-1 border-t border-slate-100 pt-1.5">
        {tools.map((tool, index) => (
          <div
            key={`${tool.tool}-${index}`}
            className="flex items-center justify-between gap-2 text-[9px] leading-4"
          >
            <div className="flex min-w-0 items-center gap-1.5">
              <Wrench className="h-2.5 w-2.5 shrink-0 text-slate-300" />
              <code className="shrink-0 font-mono text-slate-500">{tool.tool}</code>
              <span className="truncate text-slate-400">{tool.summary}</span>
            </div>
            <span className="shrink-0 tabular-nums text-slate-300">
              {tool.duration_ms}ms
            </span>
          </div>
        ))}
      </div>
    </details>
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
    <details
      className="rounded-lg border border-slate-100 bg-white/60 px-2.5 py-1.5"
      open={false}
    >
      <summary className="cursor-pointer list-none text-[10px] text-slate-400 hover:text-slate-600">
        <BookOpenCheck className="mr-1 inline h-3 w-3 text-emerald-500" />
        真题溯源 · {citations.length} 条
      </summary>
      <div className={`mt-1.5 space-y-2 border-t border-slate-100 pt-1.5 ${compact ? '' : 'max-h-[260px] overflow-y-auto scrollbar-thin'}`}>
        {citations.map((citation) => (
          <div key={citation.id} className="rounded-md bg-slate-50/60 px-2 py-1.5">
            <div className="flex flex-wrap items-center gap-1">
              <Tag tone="emerald">{citation.source}</Tag>
              {citation.grammar_tags.slice(0, 2).map((tag) => (
                <Tag key={tag} tone="slate">
                  {tag}
                </Tag>
              ))}
            </div>
            <p className="mt-1 flex gap-1.5 text-[10px] leading-5 text-slate-600">
              <Quote className="mt-0.5 h-3 w-3 shrink-0 text-slate-300" />
              {citation.text}
            </p>
          </div>
        ))}
      </div>
    </details>
  )
}
