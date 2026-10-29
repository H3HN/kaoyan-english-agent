import { useEffect, useMemo, useState } from 'react'
import { CheckCircle2, Headphones, Play, RotateCcw, Volume2, XCircle } from 'lucide-react'
import type { ListeningData } from '../lib/api'
import { Tag } from './Tag'

function speak(text: string) {
  if (!('speechSynthesis' in window)) return false
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'en-US'
  utterance.rate = 0.82
  window.speechSynthesis.speak(utterance)
  return true
}

function normalize(text: string) {
  return text.toLowerCase().replace(/[^a-z0-9' ]/g, '').replace(/\s+/g, ' ').trim()
}

export function ListeningCanvas({ data }: { data: ListeningData }) {
  const [index, setIndex] = useState(0)
  const [input, setInput] = useState('')
  const [result, setResult] = useState<boolean | null>(null)
  const [score, setScore] = useState({ correct: 0, total: 0 })
  const sentence = data.sentences[index]

  useEffect(() => {
    if (sentence) speak(sentence.text)
  }, [sentence])

  const submit = () => {
    if (!sentence || result !== null) return
    const correct = normalize(input) === normalize(sentence.text)
    setResult(correct)
    setScore((prev) => ({ correct: prev.correct + (correct ? 1 : 0), total: prev.total + 1 }))
  }

  const next = () => {
    setIndex((prev) => prev + 1)
    setInput('')
    setResult(null)
  }

  const progress = useMemo(
    () => `${Math.min(index + 1, data.sentences.length)} / ${data.sentences.length}`,
    [data.sentences.length, index],
  )

  if (!sentence) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <p className="text-lg font-bold text-slate-900">本轮听写完成</p>
        <p className="mt-1 text-sm text-slate-500">{score.correct} / {score.total} 正确</p>
        <button
          type="button"
          onClick={() => { setIndex(0); setInput(''); setResult(null); setScore({ correct: 0, total: 0 }) }}
          className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white"
        >
          <RotateCcw className="h-3.5 w-3.5" /> 再来一轮
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <section className="rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
              TIER · LISTENING DICTATION
            </p>
            <h1 className="mt-1 text-xl font-bold tracking-tight">听力听写训练场</h1>
            <p className="mt-1 text-[11px] text-slate-300">{data.source_label}</p>
          </div>
          <Tag tone="violet">{progress}</Tag>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
            <Headphones className="h-4 w-4 text-violet-500" />
            听这句，写下来
          </p>
          <button
            type="button"
            onClick={() => speak(sentence.text)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[10px] font-medium text-slate-600 hover:bg-slate-50"
          >
            <Volume2 className="h-3 w-3" /> 再听一遍
          </button>
        </div>

        <button
          type="button"
          onClick={() => speak(sentence.text)}
          className="mt-4 flex w-full min-h-[120px] flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50/60 text-slate-500 hover:border-violet-300 hover:bg-violet-50/40"
        >
          <Play className="h-7 w-7 text-violet-500" />
          <span className="mt-2 text-xs font-medium">点击播放 · 不看原文</span>
          <span className="mt-1 text-[10px] text-slate-400">建议先听两遍再写</span>
        </button>

        <form
          onSubmit={(event) => { event.preventDefault(); submit() }}
          className="mt-4 flex gap-2"
        >
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            disabled={result !== null}
            autoFocus
            placeholder="输入你听到的英文…"
            className="h-11 flex-1 rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-slate-400 disabled:bg-slate-50"
          />
          <button type="submit" disabled={!input.trim() || result !== null} className="rounded-lg bg-slate-900 px-4 text-xs font-semibold text-white disabled:bg-slate-200">
            对照
          </button>
        </form>

        {result !== null ? (
          <div className={`mt-4 rounded-xl border p-4 ${result ? 'border-emerald-200 bg-emerald-50' : 'border-red-200 bg-red-50'}`}>
            <p className="flex items-center gap-1.5 text-sm font-semibold">
              {result ? <CheckCircle2 className="h-4 w-4 text-emerald-600" /> : <XCircle className="h-4 w-4 text-red-500" />}
              {result ? '听写完全正确' : '对照原文，再听一遍'}
            </p>
            <p className="mt-2 font-serif text-[14px] leading-7 text-slate-700">{sentence.text}</p>
            <button type="button" onClick={next} className="mt-3 rounded-lg bg-slate-900 px-3 py-2 text-[11px] font-semibold text-white">
              下一句
            </button>
          </div>
        ) : null}
      </section>
    </div>
  )
}
