import { BookOpen, BookmarkPlus, ExternalLink, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { api, type WordInsightData } from '../lib/api'
import { useAppStore } from '../store/AppStore'
import { useToast } from './Toast'
import { Tag } from './Tag'

export function WordInsightCanvas({
  data,
  onDrillSentence,
}: {
  data: WordInsightData
  onDrillSentence: (text: string) => void
}) {
  const { refresh } = useAppStore()
  const toast = useToast()
  const [saved, setSaved] = useState(false)
  const [saving, setSaving] = useState(false)

  const addToWordbook = async () => {
    if (saved || saving) return
    setSaving(true)
    try {
      await api.addWord({
        spelling: data.word,
        meaning: data.basic_meaning || '待补充释义',
        source: data.is_phrase ? '短语透视' : '词汇透视',
        context: data.examples[0]?.text ?? '',
      })
      setSaved(true)
      await refresh()
      toast(`已把 ${data.word} 收入词本。`, 'success')
    } catch {
      toast('加入词本失败，请稍后重试。', 'error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-3">
      <section className="rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
              TIER 1/2 · 词汇与短语透视
            </p>
            <h1 className="mt-1 text-2xl font-serif font-semibold tracking-tight">{data.word}</h1>
            <p className="mt-1 text-[11px] text-slate-300">
              {data.is_phrase ? '短语搭配' : '单词'} · {data.level}
              {data.exam_frequency ? ` · 真题出现 ${data.exam_frequency} 次` : ''}
            </p>
          </div>
          <button
            type="button"
            onClick={() => void addToWordbook()}
            disabled={saved || saving}
            className="inline-flex items-center gap-1.5 rounded-lg bg-white px-3 py-2 text-[11px] font-semibold text-slate-900 hover:bg-slate-100 disabled:bg-white/20 disabled:text-white/60"
          >
            <BookmarkPlus className="h-3.5 w-3.5" />
            {saved ? '已收入词本' : '收入艾宾浩斯词本'}
          </button>
        </div>
      </section>

      <div className="grid gap-3 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-semibold text-slate-900">常规基础释义</p>
          <p className="mt-2 text-[15px] leading-7 text-slate-700">
            {data.basic_meaning || '大纲词库暂未收录完整释义。'}
          </p>
          {data.collocations.length ? (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {data.collocations.map((item) => (
                <Tag key={item} tone="slate">{item}</Tag>
              ))}
            </div>
          ) : null}
        </section>

        <section className="rounded-2xl border border-amber-200 border-l-4 border-l-amber-500 bg-amber-50/60 p-4 shadow-sm">
          <p className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
            <Sparkles className="h-4 w-4 text-amber-600" />
            考研高频熟词僻义 / 搭配
          </p>
          <p className="mt-2 text-[15px] leading-7 text-amber-900">
            {data.rare_meaning || '该词暂未标注熟词僻义；按基础义理解，注意上下文搭配。'}
          </p>
        </section>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-blue-500" />
          <p className="text-sm font-semibold text-slate-900">真题溯源例句</p>
          <span className="text-[10px] text-slate-400">{data.examples.length} 条</span>
        </div>
        <div className="mt-2 space-y-2">
          {data.examples.length ? data.examples.map((item) => (
            <div key={item.sentence_id} className="rounded-lg border border-slate-100 bg-slate-50/60 p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <Tag tone="emerald">{item.source}</Tag>
                <button
                  type="button"
                  onClick={() => onDrillSentence(item.text)}
                  className="inline-flex items-center gap-1 text-[10px] font-medium text-blue-600 hover:text-blue-800"
                >
                  🧬 下钻拆解此句
                  <ExternalLink className="h-3 w-3" />
                </button>
              </div>
              <p className="mt-1.5 font-serif text-[14px] leading-7 text-slate-700">{item.text}</p>
              {item.translation ? (
                <p className="mt-0.5 text-[11px] leading-5 text-slate-400">{item.translation}</p>
              ) : null}
            </div>
          )) : (
            <p className="text-xs text-slate-400">题库中暂未检索到包含该词的例句。</p>
          )}
        </div>
      </section>
    </div>
  )
}
