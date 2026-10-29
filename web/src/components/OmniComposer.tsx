import { useEffect, useRef } from 'react'
import { Send, Sparkles, X } from 'lucide-react'
import { useSession } from '../store/SessionStore'
import { useUI } from '../store/UIStore'
import { useWorkspace } from '../store/WorkspaceStore'

export interface QuickPill {
  label: string
  prompt: string
}

export function OmniComposer({
  pills,
  centered = false,
}: {
  pills: QuickPill[]
  centered?: boolean
}) {
  const { context, updateContext } = useWorkspace()
  const { typing, sendMessage } = useSession()
  const { draft, setDraft } = useUI()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const node = textareaRef.current
    if (!node) return
    node.style.height = 'auto'
    node.style.height = `${Math.min(node.scrollHeight, 140)}px`
  }, [draft])

  const send = async (text?: string) => {
    const value = (text ?? draft).trim()
    if (!value || typing) return
    setDraft('')
    await sendMessage(value)
  }

  return (
    <div className={centered ? 'mx-auto w-full max-w-3xl' : 'w-full'}>
      {context.selected_raw_text ? (
        <div className="mb-2 flex flex-wrap items-center gap-1.5 rounded-xl border border-amber-200 bg-amber-50/80 px-2.5 py-2">
          <span className="max-w-[280px] truncate text-[10px] text-amber-800">
            ✂️ 已选：{context.selected_raw_text}
          </span>
          <button
            type="button"
            onClick={() =>
              void send(`请用五步法拆解这句：${context.selected_raw_text}`)
            }
            className="rounded-md bg-slate-900 px-2 py-1 text-[9px] font-semibold text-white hover:bg-slate-800"
          >
            拆解此句语法
          </button>
          <button
            type="button"
            onClick={() =>
              void send(`请查这句里的熟词僻义：${context.selected_raw_text}`)
            }
            className="rounded-md border border-amber-200 bg-white px-2 py-1 text-[9px] font-medium text-amber-700 hover:bg-amber-50"
          >
            查句中熟词僻义
          </button>
          <button
            type="button"
            aria-label="清除划选"
            onClick={() => updateContext({ selected_raw_text: null })}
            className="ml-auto flex h-5 w-5 items-center justify-center rounded text-amber-500 hover:bg-amber-100"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      ) : null}

      <div className="mb-2 flex gap-1.5 overflow-x-auto pb-1">
        {pills.map((pill) => (
          <button
            key={pill.label}
            type="button"
            onClick={() => void send(pill.prompt)}
            disabled={typing}
            className="shrink-0 whitespace-nowrap rounded-full border border-slate-200 bg-white px-2.5 py-1 text-[10px] font-medium text-slate-500 hover:border-slate-300 hover:text-slate-800 disabled:opacity-50"
          >
            {pill.label}
          </button>
        ))}
      </div>

      <div className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-white p-1.5 shadow-sm">
        <span className="mb-1 ml-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-900 text-white">
          <Sparkles className="h-3.5 w-3.5" />
        </span>
        <textarea
          ref={textareaRef}
          rows={1}
          data-agent-input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              void send()
            }
          }}
          placeholder="问 Agent：今天读什么、拆解这句、把生词收了…"
          className="max-h-36 min-h-[40px] flex-1 resize-none bg-transparent px-1 py-2 text-[14px] leading-6 text-slate-800 outline-none placeholder:text-slate-400"
        />
        <button
          type="button"
          onClick={() => void send()}
          disabled={!draft.trim() || typing}
          className="mb-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white hover:bg-slate-800 disabled:bg-slate-200"
          aria-label="发送"
        >
          <Send className="h-3.5 w-3.5" />
        </button>
      </div>
      <p className="mt-1 px-1 text-[9px] text-slate-400">
        Enter 发送 · Shift + Enter 换行 · Agent 会自动接管主画布
      </p>
    </div>
  )
}
