import { useState } from 'react'
import { CheckCircle2, Loader2, PenLine, Sparkles } from 'lucide-react'
import { api, type WritingData, type WritingFeedback } from '../lib/api'
import { Tag } from './Tag'

const SCORE_LABELS: Record<string, string> = {
  content: '内容',
  structure: '结构',
  language: '语言',
  task: '任务完成',
}

export function WritingCanvas({ data }: { data: WritingData }) {
  const [prompt, setPrompt] = useState(data.prompt || '考研英语写作练习')
  const [draft, setDraft] = useState(data.draft || '')
  const [feedback, setFeedback] = useState<WritingFeedback | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)

  const review = async () => {
    if (draft.trim().length < 20) return
    setLoading(true)
    setError(false)
    try {
      setFeedback(await api.reviewWriting({ prompt, draft }))
    } catch {
      setError(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-3">
      <section className="rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-sm">
        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
          TIER · WRITING REVIEW
        </p>
        <h1 className="mt-1 text-xl font-bold tracking-tight">考研英语写作批改台</h1>
        <p className="mt-1 text-[11px] text-slate-300">{data.source_label}</p>
      </section>

      <div className="grid gap-3 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <label className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">
            题目
          </label>
          <input
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            className="mt-1 h-9 w-full rounded-lg border border-slate-200 px-3 text-xs outline-none focus:border-slate-400"
          />
          <label className="mt-3 block text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">
            你的作文
          </label>
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            rows={14}
            placeholder="把作文写在这里，或让 Agent 把外部文本挂载到写作画布…"
            className="mt-1 w-full resize-y rounded-xl border border-slate-200 p-3 font-serif text-[14px] leading-7 text-slate-800 outline-none focus:border-slate-400"
          />
          <div className="mt-2 flex items-center justify-between gap-2">
            <span className="text-[10px] text-slate-400">{draft.trim().split(/\s+/).filter(Boolean).length} words</span>
            <button
              type="button"
              onClick={() => void review()}
              disabled={draft.trim().length < 20 || loading}
              className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3.5 py-2 text-[11px] font-semibold text-white hover:bg-slate-800 disabled:bg-slate-200"
            >
              {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
              {loading ? '批改中…' : '批改作文'}
            </button>
          </div>
          {error ? <p className="mt-2 text-[10px] text-red-600">批改失败，请确认后端和模型配置。</p> : null}
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <PenLine className="h-4 w-4 text-violet-500" />
            <p className="text-sm font-semibold text-slate-900">最小修改反馈</p>
          </div>
          {!feedback ? (
            <div className="mt-6 rounded-xl border border-dashed border-slate-200 p-6 text-center text-xs leading-6 text-slate-400">
              写完点击“批改作文”。反馈会优先保留你的原句，只给必要修改。
            </div>
          ) : (
            <div className="mt-3 space-y-3">
              <div className="grid grid-cols-4 gap-1.5">
                {Object.entries(SCORE_LABELS).map(([key, label]) => (
                  <div key={key} className="rounded-lg bg-slate-50 p-2 text-center">
                    <p className="text-lg font-bold text-slate-900">{feedback.scores[key] ?? '—'}</p>
                    <p className="text-[9px] text-slate-400">{label}</p>
                  </div>
                ))}
              </div>
              <p className="text-[13px] leading-6 text-slate-700">{feedback.summary}</p>
              {feedback.issues.length ? (
                <div className="space-y-1.5">
                  {feedback.issues.slice(0, 6).map((issue, index) => (
                    <div key={`${issue.quote}-${index}`} className="rounded-lg border border-slate-100 bg-slate-50/70 p-2.5">
                      <div className="flex items-center gap-1.5">
                        <Tag tone={issue.type === 'grammar' ? 'red' : issue.type === 'structure' ? 'violet' : 'amber'}>{issue.type}</Tag>
                        <span className="text-[11px] font-medium text-slate-700">{issue.quote}</span>
                      </div>
                      <p className="mt-1 text-[11px] leading-5 text-slate-500">→ {issue.suggestion}</p>
                      <p className="text-[10px] leading-5 text-slate-400">{issue.reason}</p>
                    </div>
                  ))}
                </div>
              ) : null}
              {feedback.minimum_revision ? (
                <div className="rounded-lg border border-emerald-100 bg-emerald-50/60 p-3">
                  <p className="flex items-center gap-1 text-[10px] font-semibold text-emerald-800"><CheckCircle2 className="h-3 w-3" /> 最小修改版</p>
                  <p className="mt-1 font-serif text-[13px] leading-7 text-slate-700">{feedback.minimum_revision}</p>
                </div>
              ) : null}
              {feedback.next_action ? (
                <p className="rounded-lg bg-violet-50 px-3 py-2 text-[11px] leading-5 text-violet-800">下一步：{feedback.next_action}</p>
              ) : null}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
