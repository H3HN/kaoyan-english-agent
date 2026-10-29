import { useMemo, useState } from 'react'
import { BookOpen, ExternalLink, Plus, Search, Sparkles } from 'lucide-react'
import { api, type ReaderData } from '../lib/api'
import { useAppStore } from '../store/AppStore'
import { useSession } from '../store/SessionStore'
import { useWorkspace } from '../store/WorkspaceStore'
import { useToast } from './Toast'
import { Tag } from './Tag'

const WORD_RE = /([A-Za-z][A-Za-z'’\-]*)/g

export function ReaderCanvas({ data }: { data: ReaderData }) {
  const { words, addWord } = useAppStore()
  const { sendMessage } = useSession()
  const { setCanvasOp } = useWorkspace()
  const toast = useToast()
  const [selected, setSelected] = useState<{ word: string; meaning: string; loading: boolean } | null>(null)
  const known = useMemo(
    () => new Set(words.map((word) => word.spelling.toLowerCase())),
    [words],
  )
  const paragraphs = useMemo(
    () => data.text.split(/\n+/).map((item) => item.trim()).filter(Boolean),
    [data.text],
  )

  const lookup = async (word: string) => {
    setSelected({ word, meaning: '', loading: true })
    try {
      const response = await api.browseVocab({ q: word, limit: 1 })
      const meaning = response.items[0]?.basic_meaning || '词库暂未收录这个词，可按上下文理解。'
      setSelected({ word, meaning, loading: false })
    } catch {
      setSelected({ word, meaning: '释义加载失败，请确认后端已启动。', loading: false })
    }
  }

  const add = () => {
    if (!selected) return
    const result = addWord({
      spelling: selected.word,
      meaning: selected.meaning,
      source: data.source_label,
      context: paragraphs.find((item) => item.toLowerCase().includes(selected.word.toLowerCase())) ?? '',
    })
    toast(result.message, result.ok ? 'success' : 'info')
    if (result.ok) setSelected(null)
  }

  const drill = (paragraph: string) => {
    setCanvasOp('push')
    void sendMessage(`请精读这段的段落逻辑：${paragraph}`)
  }

  return (
    <div className="space-y-3">
      <section className="rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
              TIER · EXTENSIVE READING
            </p>
            <h1 className="mt-1 truncate text-xl font-bold tracking-tight">{data.title}</h1>
            <p className="mt-1 text-[11px] text-slate-300">{data.source_label}</p>
          </div>
          <Tag tone="cyan">{paragraphs.length} 段</Tag>
        </div>
      </section>

      <article className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex flex-wrap items-center gap-3 border-b border-slate-100 pb-3 text-[10px] text-slate-400">
          <span className="inline-flex items-center gap-1"><BookOpen className="h-3 w-3" /> 点虚线词查义</span>
          <span className="inline-flex items-center gap-1"><span className="rounded bg-emerald-50 px-1 text-emerald-700">已知词</span> 来自你的词本</span>
          {data.license ? <span>许可：{data.license}</span> : null}
          {data.source_url ? (
            <a href={data.source_url} target="_blank" rel="noreferrer" className="ml-auto inline-flex items-center gap-1 text-blue-600 hover:underline">
              来源 <ExternalLink className="h-2.5 w-2.5" />
            </a>
          ) : null}
        </div>

        <div className="space-y-5">
          {paragraphs.map((paragraph, paragraphIndex) => (
            <div key={`${paragraph.slice(0, 20)}-${paragraphIndex}`} className="group">
              <p className="font-serif text-[16px] leading-8 text-slate-800">
                {paragraph.split(WORD_RE).map((token, tokenIndex) => {
                  if (!/^[A-Za-z]/.test(token)) return <span key={tokenIndex}>{token}</span>
                  const normalized = token.toLowerCase()
                  const isKnown = known.has(normalized)
                  return (
                    <button
                      key={`${token}-${tokenIndex}`}
                      type="button"
                      onClick={() => void lookup(token)}
                      className={
                        isKnown
                          ? 'rounded bg-emerald-50 px-0.5 text-emerald-800 decoration-emerald-200 underline-offset-2 hover:underline'
                          : 'rounded px-0.5 decoration-dotted decoration-slate-300 underline-offset-2 hover:bg-violet-50 hover:text-violet-800 hover:underline'
                      }
                    >
                      {token}
                    </button>
                  )
                })}
              </p>
              <button
                type="button"
                onClick={() => drill(paragraph)}
                className="mt-1 inline-flex items-center gap-1 text-[9px] text-slate-300 opacity-0 transition-opacity hover:text-violet-600 group-hover:opacity-100"
              >
                <Sparkles className="h-2.5 w-2.5" /> 精读这一段
              </button>
            </div>
          ))}
        </div>
      </article>

      {selected ? (
        <section className="sticky bottom-3 z-10 rounded-xl border border-slate-200 bg-white/95 p-3 shadow-xl backdrop-blur">
          <div className="flex flex-wrap items-start gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-violet-50 text-violet-600">
              <Search className="h-4 w-4" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-serif font-semibold text-slate-900">{selected.word}</p>
              <p className="mt-0.5 text-[11px] leading-5 text-slate-500">
                {selected.loading ? '查询中…' : selected.meaning}
              </p>
            </div>
            <button
              type="button"
              onClick={add}
              disabled={selected.loading || known.has(selected.word.toLowerCase())}
              className="inline-flex items-center gap-1 rounded-lg bg-slate-900 px-3 py-2 text-[10px] font-semibold text-white disabled:bg-slate-200"
            >
              <Plus className="h-3 w-3" /> {known.has(selected.word.toLowerCase()) ? '已在词本' : '加入词本'}
            </button>
            <button type="button" onClick={() => setSelected(null)} className="px-1 text-slate-400 hover:text-slate-700">✕</button>
          </div>
        </section>
      ) : null}
    </div>
  )
}
