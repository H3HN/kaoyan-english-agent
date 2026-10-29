import { ArrowDownRight, BookOpen, Layers3, Sparkles, Star } from 'lucide-react'
import type { ParagraphData } from '../lib/api'
import { Tag } from './Tag'

export function ParagraphCanvas({
  data,
  onDrillSentence,
  onHarvest,
  onQuiz,
}: {
  data: ParagraphData
  onDrillSentence: (text: string) => void
  onHarvest: () => void
  onQuiz: () => void
}) {
  return (
    <div className="space-y-3">
      <section className="rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
              TIER 4 · 段落逻辑与语篇精读
            </p>
            <h1 className="mt-1 text-xl font-bold tracking-tight">段落逻辑精读台</h1>
            <p className="mt-1 text-[11px] text-slate-300">
              {data.source_label} · {data.sentences.length} 句
            </p>
          </div>
          <div className="flex flex-wrap gap-1.5">
            <button
              type="button"
              onClick={onHarvest}
              className="rounded-lg bg-white px-2.5 py-1.5 text-[10px] font-semibold text-slate-900 hover:bg-slate-100"
            >
              📒 一键收割本段大纲生词
            </button>
            <button
              type="button"
              onClick={onQuiz}
              className="rounded-lg border border-white/15 bg-white/5 px-2.5 py-1.5 text-[10px] text-slate-200 hover:bg-white/10"
            >
              🎯 用这段话考考我
            </button>
          </div>
        </div>
      </section>

      <div className="grid gap-3 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="rounded-2xl border border-emerald-200 border-l-4 border-l-emerald-500 bg-white p-4 shadow-sm">
          <p className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
            <Sparkles className="h-4 w-4 text-emerald-600" />
            段落核心主旨
          </p>
          <p className="mt-2 text-[15px] leading-7 text-slate-700">{data.main_idea}</p>
          <p className="mt-3 rounded-lg bg-emerald-50 px-3 py-2 text-[13px] leading-6 text-emerald-800">
            中心主旨句：{data.topic_sentence}
          </p>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
            <Layers3 className="h-4 w-4 text-violet-500" />
            句间逻辑流
          </p>
          <div className="mt-2 space-y-1.5">
            {data.sentences.map((sentence, index) => (
              <div key={sentence.index} className="flex items-center gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-100 text-[9px] font-semibold text-slate-500">
                  S{sentence.index}
                </span>
                <Tag tone={sentence.logic.includes('转折') ? 'amber' : sentence.logic.includes('结论') ? 'emerald' : 'slate'}>
                  {sentence.logic}
                </Tag>
                {index < data.sentences.length - 1 ? (
                  <ArrowDownRight className="h-3 w-3 text-slate-300" />
                ) : null}
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-blue-500" />
          <p className="text-sm font-semibold text-slate-900">逐句精读与下钻</p>
        </div>
        <div className="mt-2 space-y-2">
          {data.sentences.map((sentence) => (
            <div key={sentence.index} className="rounded-xl border border-slate-100 bg-slate-50/60 p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-1.5">
                  <Tag tone="slate">S{sentence.index}</Tag>
                  <span className="flex items-center gap-0.5 text-[10px] text-amber-500">
                    {Array.from({ length: sentence.stars }, (_, i) => (
                      <Star key={i} className="h-2.5 w-2.5 fill-current" />
                    ))}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => onDrillSentence(sentence.text)}
                  className="text-[10px] font-medium text-blue-600 hover:text-blue-800"
                >
                  🧬 五步法拆解此句 →
                </button>
              </div>
              <p className="mt-1.5 font-serif text-[14px] leading-7 text-slate-700">{sentence.text}</p>
              {sentence.translation ? (
                <p className="mt-1 text-[12px] leading-6 text-slate-500">{sentence.translation}</p>
              ) : null}
            </div>
          ))}
        </div>
      </section>

      {data.vocabulary.length ? (
        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-semibold text-slate-900">本段大纲核心词</p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {data.vocabulary.map((item) => (
              <span key={item.word} className="rounded-lg border border-amber-100 bg-amber-50 px-2 py-1 text-[11px] text-amber-800">
                {item.word} · {item.meaning}
                {item.rare_meaning ? `（僻义：${item.rare_meaning}）` : ''}
              </span>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  )
}
