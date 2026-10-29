import { useEffect, useMemo, useState } from 'react'
import { CheckCircle2, Headphones, RotateCcw, Volume2, XCircle } from 'lucide-react'
import { api, type VocabQuizItem, type VocabQuizMode } from '../lib/api'
import { useAppStore } from '../store/AppStore'
import { Tag } from './Tag'

const MODES: { id: VocabQuizMode; label: string }[] = [
  { id: 'choice', label: '选择题' },
  { id: 'spelling', label: '拼写' },
  { id: 'listening', label: '辨音' },
  { id: 'context', label: '语境填空' },
]

function speak(word: string) {
  if (!('speechSynthesis' in window)) return false
  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(word)
  utterance.lang = 'en-US'
  utterance.rate = 0.85
  window.speechSynthesis.speak(utterance)
  return true
}

export function VocabQuiz() {
  const { refresh } = useAppStore()
  const [mode, setMode] = useState<VocabQuizMode>('choice')
  const [items, setItems] = useState<VocabQuizItem[]>([])
  const [index, setIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(false)
  const [score, setScore] = useState({ correct: 0, total: 0 })
  const current = items[index]

  const load = (nextMode: VocabQuizMode) => {
    setMode(nextMode)
    setLoading(true)
    setIndex(0)
    setAnswer('')
    setResult(null)
    setScore({ correct: 0, total: 0 })
    api
      .getVocabQuiz(nextMode)
      .then((response) => setItems(response.items))
      .catch(() => setItems([]))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load('choice')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const check = async (value: string) => {
    if (!current || result !== null) return
    const correct = value.trim().toLowerCase() === current.answer.trim().toLowerCase()
    setResult(correct)
    setScore((prev) => ({ correct: prev.correct + (correct ? 1 : 0), total: prev.total + 1 }))
    try {
      await api.reviewWord(current.word, correct ? 5 : 1)
      await refresh()
    } catch {
      // Quiz feedback still works offline.
    }
  }

  const next = () => {
    setAnswer('')
    setResult(null)
    setIndex((prev) => prev + 1)
  }

  const contextWithBlank = useMemo(() => {
    if (!current?.context) return ''
    return current.context.replace(new RegExp(`\\b${current.word}\\b`, 'gi'), '____')
  }, [current])

  if (loading) {
    return <div className="py-16 text-center text-xs text-slate-400">正在生成本次词测…</div>
  }

  if (!items.length) {
    return (
      <div className="rounded-xl border border-dashed border-slate-200 bg-white p-10 text-center text-sm text-slate-400">
        词本还没有可测的词。先从阅读或 Studio 里收几个词。
      </div>
    )
  }

  if (!current) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <p className="text-lg font-bold text-slate-900">本轮完成</p>
        <p className="mt-1 text-sm text-slate-500">
          {score.correct} / {score.total} 正确
        </p>
        <button
          type="button"
          onClick={() => load(mode)}
          className="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white"
        >
          <RotateCcw className="h-3.5 w-3.5" /> 再来一轮
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex gap-1 rounded-lg border border-slate-200 bg-white p-1">
          {MODES.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => load(item.id)}
              className={`rounded-md px-2.5 py-1.5 text-[10px] font-medium ${
                mode === item.id ? 'bg-slate-900 text-white' : 'text-slate-500 hover:bg-slate-50'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
        <span className="text-[10px] text-slate-400">
          {index + 1} / {items.length} · 已答对 {score.correct}
        </span>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <Tag tone="violet">{MODES.find((item) => item.id === mode)?.label}</Tag>

        {mode === 'choice' || mode === 'listening' ? (
          <>
            {mode === 'listening' ? (
              <button type="button" onClick={() => speak(current.word)} className="mt-5 flex items-center gap-2 text-sm font-semibold text-slate-800 hover:text-violet-700">
                <Volume2 className="h-5 w-5" /> 点击听发音
              </button>
            ) : (
              <p className="mt-4 text-3xl font-serif font-semibold text-slate-900">{current.word}</p>
            )}
            <div className="mt-4 grid gap-2 sm:grid-cols-2">
              {current.options.map((option, optionIndex) => {
                const isCorrect = option === current.answer
                const chosen = answer === option
                return (
                  <button
                    key={`${option}-${optionIndex}`}
                    type="button"
                    disabled={result !== null}
                    onClick={() => {
                      setAnswer(option)
                      void check(option)
                    }}
                    className={`rounded-xl border p-3 text-left text-[13px] leading-6 ${
                      result !== null && isCorrect
                        ? 'border-emerald-300 bg-emerald-50 text-emerald-800'
                        : result !== null && chosen
                          ? 'border-red-300 bg-red-50 text-red-800'
                          : 'border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    <span className="mr-2 text-[10px] font-semibold text-slate-400">
                      {String.fromCharCode(65 + optionIndex)}
                    </span>
                    {option}
                  </button>
                )
              })}
            </div>
          </>
        ) : (
          <>
            {mode === 'context' ? (
              <p className="mt-4 font-serif text-[14px] leading-7 text-slate-700">
                {contextWithBlank || '这个词还没有原句语境，先按释义拼写。'}
              </p>
            ) : (
              <p className="mt-4 text-lg font-semibold text-slate-900">{current.meaning}</p>
            )}
            <form
              onSubmit={(event) => {
                event.preventDefault()
                void check(answer)
              }}
              className="mt-4 flex gap-2"
            >
              <input
                value={answer}
                onChange={(event) => setAnswer(event.target.value)}
                disabled={result !== null}
                autoFocus
                placeholder={mode === 'context' ? '填入缺失单词' : '输入英文拼写'}
                className="h-10 flex-1 rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-slate-400 disabled:bg-slate-50"
              />
              <button type="submit" disabled={!answer.trim() || result !== null} className="rounded-lg bg-slate-900 px-4 text-xs font-semibold text-white disabled:bg-slate-200">
                提交
              </button>
            </form>
          </>
        )}

        {result !== null ? (
          <div className={`mt-4 flex items-start gap-2 rounded-lg px-3 py-2.5 text-xs leading-6 ${result ? 'bg-emerald-50 text-emerald-800' : 'bg-red-50 text-red-800'}`}>
            {result ? <CheckCircle2 className="mt-0.5 h-4 w-4" /> : <XCircle className="mt-0.5 h-4 w-4" />}
            <div>
              <p className="font-semibold">{result ? '正确' : `错误，正确答案：${current.answer}`}</p>
              <p className="mt-0.5 text-[11px] opacity-80">{current.meaning}</p>
              {current.context ? <p className="mt-1 font-serif text-[11px] opacity-70">“{current.context}”</p> : null}
            </div>
          </div>
        ) : null}

        {result !== null ? (
          <button type="button" onClick={next} className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3 py-2 text-[11px] font-semibold text-white">
            下一题
          </button>
        ) : null}
      </section>
    </div>
  )
}
