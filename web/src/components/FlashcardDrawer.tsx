import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BookOpenCheck, Check, CircleHelp, RotateCcw, X } from 'lucide-react'
import { useAppStore } from '../store/AppStore'
import { api } from '../lib/api'
import { useUI } from '../store/UIStore'
import { useWorkspace } from '../store/WorkspaceStore'
import { unitFromSavedSentence } from '../lib/workspace'
import { Tag } from './Tag'

export function FlashcardDrawer() {
  const { flashcardOpen, setFlashcardOpen } = useUI()
  const { openWorkspaceUnit } = useWorkspace()
  const navigate = useNavigate()
  const { words, dueWords, reviewWord } = useAppStore()
  const queue = useMemo(() => (dueWords.length ? dueWords : words), [dueWords, words])
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)

  const word = queue[index % Math.max(queue.length, 1)]

  const next = (quality: number) => {
    if (word) reviewWord(word.id, quality)
    setFlipped(false)
    setIndex((prev) => (queue.length ? (prev + 1) % queue.length : 0))
  }

  const traceBack = async () => {
    if (!word?.contextSentenceId) return
    try {
      const saved = await api.getSentenceAnalysis(word.contextSentenceId)
      openWorkspaceUnit(unitFromSavedSentence(saved))
      setFlashcardOpen(false)
      navigate('/studio')
    } catch {
      // Keep the card open; no destructive fallback.
    }
  }

  useEffect(() => {
    if (!flashcardOpen) return
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null
      if (target?.tagName === 'INPUT' || target?.tagName === 'TEXTAREA') return
      if (event.key === '1') next(1)
      if (event.key === '2') next(3)
      if (event.key === '3') next(5)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  })

  if (!flashcardOpen) return null

  return (
    <>
      <button
        type="button"
        aria-label="关闭闪卡"
        className="fixed inset-0 z-[65] bg-slate-900/40 backdrop-blur-[2px]"
        onClick={() => setFlashcardOpen(false)}
      />
      <div className="fixed left-1/2 top-1/2 z-[70] w-[min(520px,calc(100vw-2rem))] -translate-x-1/2 -translate-y-1/2 rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-50 text-amber-600">
              <BookOpenCheck className="h-4 w-4" />
            </span>
            <div>
              <p className="text-sm font-semibold text-slate-900">艾宾浩斯闪卡</p>
              <p className="text-[10px] text-slate-400">
                {queue.length ? `${index + 1} / ${queue.length}` : '暂无单词'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => setFlashcardOpen(false)}
            className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700"
            aria-label="关闭"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {word ? (
          <>
            <button
              type="button"
              onClick={() => setFlipped((prev) => !prev)}
              className="mt-4 flex min-h-[220px] w-full flex-col items-center justify-center rounded-xl border border-slate-200 bg-gradient-to-b from-slate-50 to-white p-6 text-center transition-colors hover:border-slate-300"
            >
              <span className="text-3xl font-serif font-semibold text-slate-900">{word.spelling}</span>
              {word.phonetic ? <span className="mt-1 text-xs text-slate-400">{word.phonetic}</span> : null}
              {word.contextSentenceEn ? (
                <p className="mt-2 line-clamp-2 max-w-md text-center font-serif text-[11px] leading-5 text-slate-500">
                  “{word.contextSentenceEn}”
                </p>
              ) : null}
              <div className="mt-3 flex flex-wrap justify-center gap-1.5">
                <Tag tone={word.isOutline ? 'emerald' : 'amber'}>
                  {word.isOutline ? '大纲词' : '超纲词'}
                </Tag>
                <Tag tone="slate">{word.source || '未标注出处'}</Tag>
              </div>
              {flipped ? (
                <div className="mt-4 space-y-2">
                  <p className="text-sm leading-7 text-slate-700">{word.meaning}</p>
                  {word.contextSentenceId ? (
                    <button
                      type="button"
                      onClick={() => void traceBack()}
                      className="rounded-md border border-blue-200 bg-blue-50 px-2.5 py-1 text-[10px] font-medium text-blue-700 hover:bg-blue-100"
                    >
                      🔗 穿回原句精析台
                    </button>
                  ) : null}
                  <p className="text-[10px] text-slate-400">点击卡片翻回正面 · 1/2/3 快速评分</p>
                </div>
              ) : (
                <p className="mt-6 flex items-center gap-1.5 text-[11px] text-slate-400">
                  <CircleHelp className="h-3.5 w-3.5" /> 点击翻转查看释义
                </p>
              )}
            </button>

            <div className="mt-3 grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => next(1)}
                className="rounded-lg border border-red-200 bg-red-50 px-2 py-2 text-[11px] font-medium text-red-700 hover:bg-red-100"
              >
                忘记了
              </button>
              <button
                type="button"
                onClick={() => next(3)}
                className="rounded-lg border border-amber-200 bg-amber-50 px-2 py-2 text-[11px] font-medium text-amber-700 hover:bg-amber-100"
              >
                有点模糊
              </button>
              <button
                type="button"
                onClick={() => next(5)}
                className="rounded-lg border border-emerald-200 bg-emerald-50 px-2 py-2 text-[11px] font-medium text-emerald-700 hover:bg-emerald-100"
              >
                牢记
              </button>
            </div>
            <div className="mt-2 flex justify-end">
              <button
                type="button"
                onClick={() => setIndex(0)}
                className="inline-flex items-center gap-1 text-[10px] text-slate-400 hover:text-slate-600"
              >
                <RotateCcw className="h-3 w-3" /> 回到第一张
              </button>
            </div>
          </>
        ) : (
          <div className="mt-6 rounded-xl border border-dashed border-slate-200 p-8 text-center text-xs text-slate-400">
            单词本还是空的，先在阅读页让 Agent 整理生词。
          </div>
        )}
        <div className="mt-3 flex items-center justify-center gap-1 text-[9px] text-slate-400">
          <Check className="h-3 w-3" /> 评分会写回 SQLite，更新下次复习时间
        </div>
      </div>
    </>
  )
}
