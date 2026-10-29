import { useEffect, useState } from 'react'
import { ArrowRight, BookOpen, Clock, FileQuestion } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { api, type PassageSummary } from '../lib/api'

export default function ReadingHome() {
  const [passages, setPassages] = useState<PassageSummary[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    api
      .getPassages()
      .then((response) => setPassages(response.items))
      .catch(() => setPassages([]))
      .finally(() => setLoading(false))
  }, [])

  const open = (passage: PassageSummary) => {
    navigate(
      `/reading?year=${passage.year}&exam=${encodeURIComponent(passage.exam_type)}&text=${passage.text_number}`,
    )
  }

  return (
    <div className="space-y-4">
      <section className="rounded-2xl bg-slate-900 px-6 py-6 text-white shadow-sm">
        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
          READING ARENA
        </p>
        <h1 className="mt-1 text-2xl font-bold tracking-tight">先选一套题，再开始阅读</h1>
        <p className="mt-1 max-w-2xl text-xs leading-6 text-slate-300">
          不自动打开默认文章。选一套已发布真题后，才会进入计时阅读与选项诊断。
        </p>
      </section>

      <div className="flex items-center justify-between px-1">
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
          已发布真题
        </p>
        <span className="text-[10px] text-slate-400">{passages.length} 篇</span>
      </div>

      {loading ? (
        <div className="rounded-xl border border-slate-200 bg-white py-16 text-center text-xs text-slate-400">加载中…</div>
      ) : passages.length ? (
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {passages.map((passage) => (
            <button
              key={passage.id}
              type="button"
              onClick={() => open(passage)}
              className="group rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md"
            >
              <div className="flex items-start justify-between gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-blue-600"><BookOpen className="h-4 w-4" /></span>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[9px] text-slate-500">{passage.year}</span>
              </div>
              <p className="mt-3 text-sm font-semibold text-slate-900">{passage.exam_type} · Text {passage.text_number}</p>
              <p className="mt-1 text-[10px] text-slate-400">
                {passage.sentence_count} 句 · {passage.question_count} 题
              </p>
              <div className="mt-3 flex items-center gap-2 text-[9px] text-slate-400">
                <span className="inline-flex items-center gap-1"><Clock className="h-2.5 w-2.5" /> 计时训练</span>
                <span className="inline-flex items-center gap-1"><FileQuestion className="h-2.5 w-2.5" /> 陷阱诊断</span>
              </div>
              <span className="mt-3 inline-flex items-center gap-1 text-[10px] font-medium text-blue-600">开始阅读 <ArrowRight className="h-3 w-3" /></span>
            </button>
          ))}
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-slate-200 bg-white p-10 text-center text-xs text-slate-400">还没有已发布真题。</div>
      )}
    </div>
  )
}
