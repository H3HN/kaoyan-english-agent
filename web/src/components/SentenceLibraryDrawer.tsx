import { useEffect, useState } from 'react'
import { BookMarked, Loader2, Star, X } from 'lucide-react'
import { api, type SentenceLibraryItem, type SentenceLibraryResponse } from '../lib/api'
import { Tag } from './Tag'

export function SentenceLibraryDrawer({
  open,
  onClose,
  onSelect,
}: {
  open: boolean
  onClose: () => void
  onSelect: (item: SentenceLibraryItem) => void
}) {
  const [tab, setTab] = useState<'saved' | 'featured'>('saved')
  const [data, setData] = useState<SentenceLibraryResponse>({ featured: [], saved: [] })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!open) return
    setLoading(true)
    api
      .getSentenceLibrary()
      .then(setData)
      .catch(() => setData({ featured: [], saved: [] }))
      .finally(() => setLoading(false))
  }, [open])

  if (!open) return null
  const items = tab === 'saved' ? data.saved : data.featured

  return (
    <>
      <button
        type="button"
        aria-label="关闭句库"
        className="fixed inset-0 z-[55] bg-slate-900/30 backdrop-blur-[1px]"
        onClick={onClose}
      />
      <aside className="fixed right-0 top-0 z-[60] flex h-full w-[min(460px,92vw)] flex-col border-l border-slate-200 bg-white shadow-2xl">
        <header className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <div>
            <p className="text-sm font-semibold text-slate-900">📚 句库抽屉</p>
            <p className="mt-0.5 text-[10px] text-slate-400">收藏句与真题精选句</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700"
            aria-label="关闭"
          >
            <X className="h-4 w-4" />
          </button>
        </header>

        <div className="flex gap-1 border-b border-slate-100 p-2">
          <button
            type="button"
            onClick={() => setTab('saved')}
            className={`flex-1 rounded-lg px-3 py-1.5 text-[11px] font-medium ${
              tab === 'saved' ? 'bg-slate-900 text-white' : 'text-slate-500 hover:bg-slate-50'
            }`}
          >
            ⭐ 我的收藏句 ({data.saved.length})
          </button>
          <button
            type="button"
            onClick={() => setTab('featured')}
            className={`flex-1 rounded-lg px-3 py-1.5 text-[11px] font-medium ${
              tab === 'featured' ? 'bg-slate-900 text-white' : 'text-slate-500 hover:bg-slate-50'
            }`}
          >
            🔥 真题经典长难句 ({data.featured.length})
          </button>
        </div>

        <div className="min-h-0 flex-1 space-y-2 overflow-y-auto p-3">
          {loading ? (
            <div className="flex items-center justify-center gap-2 py-8 text-xs text-slate-400">
              <Loader2 className="h-4 w-4 animate-spin" /> 正在读取句库…
            </div>
          ) : items.length ? (
            items.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelect(item)}
                className="w-full rounded-xl border border-slate-200 bg-white p-3 text-left transition-all hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-sm"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="flex items-center gap-1 text-[9px] font-medium text-slate-400">
                    {item.source_type === 'USER_SAVED' ? (
                      <Star className="h-3 w-3 text-amber-500" />
                    ) : (
                      <BookMarked className="h-3 w-3 text-blue-500" />
                    )}
                    {item.source_label}
                  </span>
                  <span className="text-[9px] text-slate-300">切换</span>
                </div>
                <p className="mt-1.5 line-clamp-2 font-serif text-[13px] leading-6 text-slate-700">
                  {item.preview}
                </p>
                <div className="mt-1.5 flex flex-wrap gap-1">
                  {item.grammar_tags.slice(0, 3).map((tag) => (
                    <Tag key={tag} tone="violet">{tag}</Tag>
                  ))}
                </div>
              </button>
            ))
          ) : (
            <div className="rounded-xl border border-dashed border-slate-200 p-6 text-center text-xs text-slate-400">
              {tab === 'saved' ? '还没有收藏句，先让 Agent 精析一句并存入句库。' : '题库暂无已发布精选句。'}
            </div>
          )}
        </div>
      </aside>
    </>
  )
}
