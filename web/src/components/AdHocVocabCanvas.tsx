import { ArrowLeft, BookOpenCheck, Sparkles } from 'lucide-react'
import type { AdHocVocabData } from '../lib/api'
import { Tag } from './Tag'

export function AdHocVocabCanvas({
  data,
  onClose,
}: {
  data: AdHocVocabData
  onClose: () => void
}) {
  const words = data.words?.length
    ? data.words
    : data.added.map((item) => ({ ...item, status: 'new' as const }))

  return (
    <div className="space-y-3">
      <section className="rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
              AD-HOC VOCAB · 实时提取
            </p>
            <h1 className="mt-1 text-xl font-bold tracking-tight">外源文本生词视图</h1>
            <p className="mt-1 text-[11px] text-slate-300">
              命中大纲词 {data.total} 个 · 新增入库 {data.added.length} 个 · 跳过已掌握 {data.skipped} 个
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center gap-1.5 rounded-lg border border-white/15 bg-white/5 px-3 py-1.5 text-[11px] text-slate-200 hover:bg-white/10"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            退出本次提取
          </button>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2">
          <BookOpenCheck className="h-4 w-4 text-amber-500" />
          <p className="text-sm font-semibold text-slate-900">文本切片</p>
        </div>
        <p className="mt-2 line-clamp-4 font-serif text-[14px] leading-7 text-slate-600">
          {data.source_text}
        </p>
      </section>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {words.length ? words.map((item, index) => (
          <section
            key={`${item.word}-${index}`}
            className="rounded-xl border border-slate-200 border-l-4 border-l-amber-400 bg-white p-4 shadow-sm"
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-lg font-serif font-semibold text-slate-900">{item.word}</p>
              <Tag tone={item.status === 'existing' ? 'slate' : 'amber'}>
                {item.status === 'existing' ? '已在词本' : '新词'}
              </Tag>
            </div>
            <p className="mt-2 text-[14px] leading-6 text-slate-600">{item.meaning}</p>
            {item.rare ? (
              <p className="mt-2 rounded-md bg-amber-50 px-2 py-1.5 text-[13px] leading-5 text-amber-800">
                熟词僻义：{item.rare}
              </p>
            ) : null}
            <p className="mt-2 text-[10px] text-slate-400">{item.source ?? '自定义输入'}</p>
          </section>
        )) : (
          <div className="rounded-xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-400 sm:col-span-2 lg:col-span-3">
            这段文本里的大纲词都已在词本中，没有新增。
          </div>
        )}
      </div>

      <div className="flex items-center gap-1.5 px-1 text-[10px] text-slate-400">
        <Sparkles className="h-3 w-3 text-amber-500" />
        本页是本次外源提取的临时视图；词条已真实写入艾宾浩斯词本。
      </div>
    </div>
  )
}
