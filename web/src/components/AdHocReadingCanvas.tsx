import { ArrowLeft, CheckCircle2, ScanText, Target } from 'lucide-react'
import type { AdHocReadingData } from '../lib/api'
import { Tag } from './Tag'

export function AdHocReadingCanvas({
  data,
  onClose,
}: {
  data: AdHocReadingData
  onClose: () => void
}) {
  const keys = ['A', 'B', 'C', 'D']
  return (
    <div className="space-y-3">
      <section className="rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
              AD-HOC READING · 实时验伪
            </p>
            <h1 className="mt-1 text-xl font-bold tracking-tight">外源阅读选项验伪</h1>
            <p className="mt-1 text-[11px] text-slate-300">
              {data.source_label} · {data.question_type}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex items-center gap-1.5 rounded-lg border border-white/15 bg-white/5 px-3 py-1.5 text-[11px] text-slate-200 hover:bg-white/10"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            退出本次验伪
          </button>
        </div>
      </section>

      <div className="grid gap-3 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <ScanText className="h-4 w-4 text-blue-500" />
            <p className="text-sm font-semibold text-slate-900">外源原文</p>
          </div>
          <p className="mt-2 whitespace-pre-line font-serif text-[14.5px] leading-7 text-slate-700">
            {data.passage_text || '这段输入没有单独提供原文，请结合题干定位。'}
          </p>
        </section>

        <section className="rounded-2xl border border-slate-200 border-l-4 border-l-blue-500 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <Target className="h-4 w-4 text-blue-600" />
            <p className="text-sm font-semibold text-slate-900">题干</p>
            <Tag tone="blue">{data.question_type}</Tag>
          </div>
          <p className="mt-2 text-[15px] leading-7 text-slate-800">{data.question_text}</p>
          {data.correct_answer ? (
            <p className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-emerald-50 px-2 py-1 text-[11px] text-emerald-700">
              <CheckCircle2 className="h-3 w-3" />
              当前判断：{data.correct_answer} 为正确项
            </p>
          ) : null}
        </section>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-semibold text-slate-900">选项验伪</p>
          <span className="text-[10px] text-slate-400">陷阱标签由 Agent 对外源文本实时判断</span>
        </div>
        <div className="mt-3 grid gap-2 sm:grid-cols-2">
          {keys.map((key) => {
            const info = data.analysis[key] ?? { trapType: '待分析', explanation: '暂无解释' }
            const correct = key === data.correct_answer || info.trapType === '正确'
            return (
              <div
                key={key}
                className={`rounded-xl border p-3 ${
                  correct
                    ? 'border-emerald-200 bg-emerald-50/50'
                    : 'border-slate-200 bg-slate-50/50'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-md bg-white text-[11px] font-bold text-slate-700 ring-1 ring-slate-200">
                    {key}
                  </span>
                  <Tag tone={correct ? 'emerald' : 'red'}>{info.trapType}</Tag>
                </div>
                <p className="mt-2 text-[14px] leading-6 text-slate-700">{data.options[key]}</p>
                <p className="mt-1 text-[12px] leading-5 text-slate-500">{info.explanation}</p>
              </div>
            )
          })}
        </div>
      </section>

      {data.steps.length ? (
        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-sm font-semibold text-slate-900">解题路径</p>
          <div className="mt-2 space-y-1.5">
            {data.steps.map((step, index) => (
              <p key={`${step}-${index}`} className="flex items-start gap-2 text-[13.5px] leading-6 text-slate-600">
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-100 text-[10px] font-semibold text-slate-500">
                  {index + 1}
                </span>
                {step}
              </p>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  )
}
