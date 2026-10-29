import { useEffect, useMemo, useRef, useState } from 'react'
import {
  ArrowRight,
  CheckCircle2,
  Clock,
  Loader2,
  Sparkles,
  X,
  XCircle,
} from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import { CitationList, ToolTrace } from '../components/ToolTrace'
import { Tag, type Tone } from '../components/Tag'
import { TrapMethodCardView } from '../components/TrapMethodCardView'
import type { QuestionType } from '../data/content'
import { api, type FullQuestion, type LearnerProfile, type OptionWorkflow, type TrapMethodCard } from '../lib/api'
import { useAppStore } from '../store/AppStore'
import { useSession } from '../store/SessionStore'
import { useWorkspace } from '../store/WorkspaceStore'

type OptionKey = 'A' | 'B' | 'C' | 'D'
const optionKeys: OptionKey[] = ['A', 'B', 'C', 'D']

type OptionQuestion = FullQuestion

interface PassageGroup {
  key: string
  year: number
  examType: string
  textNumber: number
  passage: string
  questions: OptionQuestion[]
}

interface Attempt {
  answer: OptionKey
  isCorrect: boolean
}

const borderMap: Record<Tone, string> = {
  blue: 'border-l-blue-500',
  emerald: 'border-l-emerald-500',
  cyan: 'border-l-cyan-500',
  amber: 'border-l-amber-500',
  violet: 'border-l-violet-500',
  red: 'border-l-red-500',
  slate: 'border-l-slate-300',
}

function trapTone(trap: string): Tone {
  if (trap === '正确') return 'emerald'
  if (trap.includes('范围')) return 'amber'
  if (trap === '无中生有') return 'cyan'
  if (trap === '过度推理' || trap === '张冠李戴') return 'violet'
  if (trap === '偷换概念' || trap === '正反混淆' || trap === '过于绝对') {
    return 'red'
  }
  return 'slate'
}

function normalize(text: string) {
  return text.replace(/\s+/g, ' ').trim().toLowerCase()
}

function splitSentences(text: string) {
  return text
    .split(/(?<=[.!?])\s+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function buildParagraphs(text: string) {
  const explicit = text
    .split(/\n{2,}/)
    .map((item) => item.trim())
    .filter(Boolean)
  // Preserve explicit paragraph boundaries; do not invent three paragraphs.
  return explicit.length ? explicit : [text]
}

interface ReadingSummary {
  duration: number
  answered: number
  correct: number
  total: number
}

export default function OptionsPage() {
  const [allQuestions, setAllQuestions] = useState<OptionQuestion[]>([])
  const [selection, setSelection] = useState({
    year: 0,
    examType: '',
    textNumber: 0,
  })
  const [activeQuestionId, setActiveQuestionId] = useState('')
  const [loadError, setLoadError] = useState(false)
  const [loading, setLoading] = useState(true)
  const [attempts, setAttempts] = useState<Record<string, Attempt>>({})
  const [selected, setSelected] = useState<OptionKey | null>(null)
  const [showAnalysis, setShowAnalysis] = useState(false)
  const [agentFeedback, setAgentFeedback] = useState<OptionWorkflow | null>(null)
  const [agentError, setAgentError] = useState(false)
  const [searchParams] = useSearchParams()
  const highlightRef = useRef<HTMLSpanElement>(null)
  const activeQuestionRef = useRef<string | undefined>(undefined)
  const { addRecord } = useAppStore()
  const { context, updateContext } = useWorkspace()
  const { sendMessage, sendAutoEvent } = useSession()
  const [agentHighlight, setAgentHighlight] = useState('')
  const [trapCard, setTrapCard] = useState<TrapMethodCard | null>(null)
  const [learnerProfile, setLearnerProfile] = useState<LearnerProfile | null>(null)
  const [sessionStartedAt, setSessionStartedAt] = useState(() => new Date().toISOString())
  const [elapsed, setElapsed] = useState(0)
  const [summary, setSummary] = useState<ReadingSummary | null>(null)
  const autoFinishedRef = useRef('')

  useEffect(() => {
    let alive = true
    setLoading(true)
    setLoadError(false)
    setAllQuestions([])
    setActiveQuestionId('')
    api
      .getQuestionsFull()
      .then((response) => {
        if (!alive) return
        setAllQuestions(response.items)
        const paramYear = Number(searchParams.get('year') ?? 0)
        const paramText = Number(searchParams.get('text') ?? 0)
        const paramExam = searchParams.get('exam') ?? ''
        const paramQuestion = searchParams.get('question_id') ?? searchParams.get('question') ?? ''
        const linkedQuestion = paramQuestion
          ? response.items.find((item) => item.id === paramQuestion)
          : undefined
        const linked = linkedQuestion ?? (paramYear && paramText
          ? response.items.find(
              (item) =>
                item.year === paramYear &&
                item.textNumber === paramText &&
                (!paramExam || item.examType === paramExam),
            )
          : undefined)
        if (linked) {
          setSelection({
            year: linked.year,
            examType: linked.examType,
            textNumber: linked.textNumber,
          })
          setActiveQuestionId(linked.id)
          return
        }
        const imported = response.items
          .filter((item) => item.id.startsWith('auto_'))
          .sort(
            (a, b) =>
              b.year - a.year ||
              a.textNumber - b.textNumber ||
              a.number - b.number,
          )
        const first = imported[0] ?? response.items[0]
        if (first) {
          setSelection({
            year: first.year,
            examType: first.examType,
            textNumber: first.textNumber,
          })
          setActiveQuestionId(first.id)
        }
      })
      .catch(() => {
        if (alive) setLoadError(true)
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => {
      alive = false
    }
  }, [searchParams])

  const groups = useMemo<PassageGroup[]>(() => {
    const map = new Map<string, OptionQuestion[]>()
    allQuestions.forEach((question) => {
      const key = `${question.year}|${question.examType}|${question.textNumber}`
      const bucket = map.get(key) ?? []
      bucket.push(question)
      map.set(key, bucket)
    })
    return Array.from(map.entries()).map(([key, items]) => {
      const sorted = [...items].sort((a, b) => a.number - b.number)
      const imported = sorted.filter((item) => item.id.startsWith('auto_'))
      const chosen =
        imported.length > sorted.length - imported.length ? imported : sorted
      const first = chosen[0]
      return {
        key,
        year: first.year,
        examType: first.examType,
        textNumber: first.textNumber,
        passage:
          chosen.find((item) => item.passage)?.passage ??
          first.sourceSentence,
        questions: chosen,
      }
    })
  }, [allQuestions])

  const years = useMemo(
    () => Array.from(new Set(groups.map((item) => item.year))).sort((a, b) => b - a),
    [groups],
  )
  const examTypes = useMemo(
    () =>
      Array.from(
        new Set(
          groups
            .filter((item) => item.year === selection.year)
            .map((item) => item.examType),
        ),
      ),
    [groups, selection.year],
  )
  const texts = useMemo(
    () =>
      groups
        .filter(
          (item) =>
            item.year === selection.year &&
            item.examType === selection.examType,
        )
        .map((item) => item.textNumber)
        .sort((a, b) => a - b),
    [groups, selection.examType, selection.year],
  )
  const currentGroup =
    groups.find(
      (item) =>
        item.year === selection.year &&
        item.examType === selection.examType &&
        item.textNumber === selection.textNumber,
    ) ?? groups[0]
  const activeQuestion =
    currentGroup?.questions.find((item) => item.id === activeQuestionId) ??
    currentGroup?.questions[0]
  const steps = activeQuestion?.steps ?? []
  const hasCompleteAnalysis = optionKeys.every((key) => {
    const analysis = activeQuestion?.analysis?.[key]
    return Boolean(analysis?.trapType?.trim() && analysis.explanation?.trim())
  })
  const isBasicPractice = !hasCompleteAnalysis || steps.length === 0

  useEffect(() => {
    activeQuestionRef.current = activeQuestion?.id
    if (!activeQuestion) return
    const attempt = attempts[activeQuestion.id]
    setSelected(attempt?.answer ?? null)
    setShowAnalysis(Boolean(attempt))
    setAgentFeedback(null)
    setAgentError(false)
    setAgentHighlight('')
    setTrapCard(null)
    // Intentionally reaction to question changes; attempts is read once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeQuestion?.id])

  useEffect(() => {
    if (!currentGroup || !activeQuestion) return
    updateContext({
      current_route: '/reading',
      active_passage_id: activeQuestion.passageId,
      active_passage_label: `${currentGroup.year} ${currentGroup.examType} Text ${currentGroup.textNumber}`,
      active_question_id: activeQuestion.id,
      active_sentence_id: activeQuestion.sourceSentenceId ?? null,
    })
  }, [currentGroup?.key, activeQuestion?.id, activeQuestion?.passageId, activeQuestion?.sourceSentenceId, updateContext])

  useEffect(() => {
    if (!activeQuestion || searchParams.get('reveal') !== '1') return
    setShowAnalysis(true)
    if (searchParams.get('highlight') === '1') {
      setAgentHighlight(activeQuestion.sourceSentence)
    }
  }, [activeQuestion?.id, activeQuestion?.sourceSentence, searchParams])

  useEffect(() => {
    if (summary) return
    const id = window.setInterval(() => {
      setElapsed(
        Math.max(0, Math.floor((Date.now() - new Date(sessionStartedAt).getTime()) / 1000)),
      )
    }, 1000)
    return () => window.clearInterval(id)
  }, [sessionStartedAt, summary])

  useEffect(() => {
    setSessionStartedAt(new Date().toISOString())
    setElapsed(0)
    setSummary(null)
    autoFinishedRef.current = ''
  }, [currentGroup?.key])

  useEffect(() => {
    if (!currentGroup || summary) return
    const answered = currentGroup.questions.filter((question) => attempts[question.id]).length
    if (answered < currentGroup.questions.length) return
    if (autoFinishedRef.current === currentGroup.key) return
    autoFinishedRef.current = currentGroup.key
    void finishSession()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempts, currentGroup?.key, summary])

  useEffect(() => {
    if (!showAnalysis) return
    highlightRef.current?.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
    })
  }, [showAnalysis, activeQuestion?.id, agentHighlight])

  const finishSession = async () => {
    if (!currentGroup || summary) return
    const answeredQuestions = currentGroup.questions.filter((question) => attempts[question.id])
    const correctCount = answeredQuestions.filter((question) => attempts[question.id]?.isCorrect).length
    const duration = Math.max(0, Math.floor((Date.now() - new Date(sessionStartedAt).getTime()) / 1000))
    const next: ReadingSummary = {
      duration,
      answered: answeredQuestions.length,
      correct: correctCount,
      total: currentGroup.questions.length,
    }
    setSummary(next)
    try {
      await api.saveReadingSession({
        passage_id: currentGroup.questions[0]?.passageId ?? '',
        started_at: sessionStartedAt,
        duration_seconds: duration,
        answered: next.answered,
        correct: next.correct,
      })
    } catch {
      // The summary remains useful even if the local backend is offline.
    }
  }

  const paragraphs = useMemo(
    () => buildParagraphs(currentGroup?.passage ?? ''),
    [currentGroup?.passage],
  )

  const applySelection = (next: {
    year: number
    examType: string
    textNumber: number
  }) => {
    setSelection(next)
    const first = groups.find(
      (item) =>
        item.year === next.year &&
        item.examType === next.examType &&
        item.textNumber === next.textNumber,
    )
    if (first) setActiveQuestionId(first.questions[0].id)
  }

  const handleSubmit = () => {
    if (!selected || !activeQuestion || showAnalysis) return
    const isCorrect = selected === activeQuestion.correctAnswer
    const record = {
      questionId: activeQuestion.id,
      questionType: activeQuestion.questionType as QuestionType,
      userAnswer: selected,
      correctAnswer: activeQuestion.correctAnswer,
    }
    addRecord(record)
    setAttempts((prev) => ({
      ...prev,
      [activeQuestion.id]: { answer: selected, isCorrect },
    }))
    setShowAnalysis(true)
    setAgentFeedback(null)
    setAgentError(false)
    if (!isCorrect) {
      void sendAutoEvent({
        event_type: 'QUESTION_SUBMITTED',
        question_id: activeQuestion.id,
        user_choice: selected,
        correct_choice: activeQuestion.correctAnswer as 'A' | 'B' | 'C' | 'D',
        is_correct: false,
        trap_type: activeQuestion.analysis?.[selected]?.trapType ?? undefined,
      })
    }
    if (!isCorrect) {
      const trap = activeQuestion.analysis?.[selected]?.trapType
      if (trap) {
        void api.getTrapCard(trap).then(setTrapCard).catch(() => {})
      }
      void api.getLearnerProfile().then(setLearnerProfile).catch(() => {})
    }
    const questionId = activeQuestion.id
    if (isBasicPractice || activeQuestion.reviewStatus === 'practice') {
      // Basic practice uses the saved answer only; do not generate missing analysis.
      void api.addRecord(record).catch(() => {
        if (activeQuestionRef.current === questionId) setAgentError(true)
      })
      return
    }
    api
      .runOptions(questionId, selected)
      .then((feedback) => {
        if (activeQuestionRef.current === questionId) setAgentFeedback(feedback)
      })
      .catch(() => {
        if (activeQuestionRef.current === questionId) setAgentError(true)
      })
  }

  const currentAttempt = activeQuestion
    ? attempts[activeQuestion.id]
    : undefined

  if (!currentGroup || !activeQuestion) {
    return (
      <div role="status" className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white p-8 text-sm text-slate-500">
        {loadError ? (
          '暂时无法读取题库，请稍后重试。'
        ) : loading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
            正在加载题库…
          </>
        ) : (
          '暂无已发布的真题，发布后即可开始训练。'
        )}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-slate-800 px-6 py-4 text-white">
        <div className="flex items-baseline gap-3">
          <h1 className="text-xl font-bold tracking-tight">真题联读室</h1>
          <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
            OPTION TRAPS
          </span>
        </div>
        <span className="text-xs text-slate-300">
          {currentGroup.year} {currentGroup.examType} · Text{' '}
          {currentGroup.textNumber} · {currentGroup.questions.length} 题
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2 rounded-xl border border-slate-200 bg-white p-2.5 shadow-sm">
        <select
          value={selection.year}
          onChange={(event) => {
            const year = Number(event.target.value)
            const examType =
              groups.find((item) => item.year === year)?.examType ??
              selection.examType
            const textNumber =
              groups.find(
                (item) => item.year === year && item.examType === examType,
              )?.textNumber ?? 1
            applySelection({ year, examType, textNumber })
          }}
          aria-label="年份"
          className="h-9 rounded-lg border border-slate-200 bg-white px-3 text-xs font-medium text-slate-700 outline-none"
        >
          {years.map((year) => (
            <option key={year} value={year}>
              {year} 年
            </option>
          ))}
        </select>
        <select
          value={selection.examType}
          onChange={(event) => {
            const examType = event.target.value
            const textNumber =
              groups.find(
                (item) =>
                  item.year === selection.year && item.examType === examType,
              )?.textNumber ?? 1
            applySelection({ ...selection, examType, textNumber })
          }}
          aria-label="试卷"
          className="h-9 rounded-lg border border-slate-200 bg-white px-3 text-xs font-medium text-slate-700 outline-none"
        >
          {examTypes.map((examType) => (
            <option key={examType} value={examType}>
              {examType}
            </option>
          ))}
        </select>

        <div className="inline-flex rounded-lg bg-slate-100 p-1">
          {texts.map((textNumber) => (
            <button
              key={textNumber}
              type="button"
              onClick={() =>
                applySelection({ ...selection, textNumber })
              }
              className={`rounded-md px-3 py-1.5 text-[11px] font-medium transition-colors ${
                selection.textNumber === textNumber
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
              aria-pressed={selection.textNumber === textNumber}
            >
              Text {textNumber}
            </button>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-2">
          <button
            type="button"
            onClick={() => void sendMessage('把这篇阅读里的生词整理入库。')}
            className="inline-flex items-center gap-1.5 rounded-lg border border-amber-200 bg-amber-50 px-2.5 py-1.5 text-[10px] font-semibold text-amber-700 hover:bg-amber-100"
          >
            <Sparkles className="h-3 w-3" />
            一键提炼本篇生词
          </button>
          <span className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-1 text-[10px] text-slate-500 tabular-nums">
            <Clock className="h-3 w-3" />
            {String(Math.floor(elapsed / 60)).padStart(2, '0')}:{String(elapsed % 60).padStart(2, '0')}
          </span>
          <Tag tone="slate">{currentGroup.questions.length} 题</Tag>
          <button
            type="button"
            onClick={() => void finishSession()}
            className="rounded-md border border-slate-200 bg-white px-2 py-1.5 text-[10px] font-medium text-slate-500 hover:border-slate-300 hover:text-slate-800"
          >
            结束训练
          </button>
        </div>
      </div>

      <div className="grid gap-5 lg:h-[calc(100dvh-250px)] lg:min-h-[520px] lg:grid-cols-12">
        <section className="max-h-[520px] overflow-y-auto rounded-xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-6 lg:max-h-none lg:h-full">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <Tag tone="blue">
                {currentGroup.year} {currentGroup.examType}
              </Tag>
              <span className="text-[11px] text-slate-400">
                Text {currentGroup.textNumber}
              </span>
            </div>
            <span className="text-[11px] text-slate-400">
              {currentGroup.questions.length} 题
            </span>
          </div>

          <div className="mt-5 space-y-5">
            {paragraphs.map((paragraph, paragraphIndex) => (
              <div key={`${paragraphIndex}-${paragraph.slice(0, 20)}`}>
                <div className="mb-1.5 flex items-center justify-between gap-2">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
                    P{paragraphIndex + 1}
                  </p>
                  <button
                    type="button"
                    onClick={() =>
                      void sendMessage(`请精读这段的段落逻辑：${paragraph}`)
                    }
                    className="rounded-md border border-slate-200 bg-white px-2 py-1 text-[9px] font-medium text-slate-500 hover:border-slate-300 hover:text-slate-800"
                  >
                    📑 精读本段逻辑
                  </button>
                </div>
                <p className="font-serif text-[14.5px] leading-[1.95] text-slate-700">
                  {splitSentences(paragraph).map((sentence, sentenceIndex) => {
                    const target = agentHighlight
                      || (showAnalysis && activeQuestion.locationStatus === 'exact_quote'
                        ? activeQuestion.sourceSentence
                        : '')
                    const isTarget =
                      Boolean(target) &&
                      (normalize(sentence).includes(normalize(target)) ||
                        normalize(target).includes(normalize(sentence)))
                    return (
                      <span
                        key={`${sentenceIndex}-${sentence.slice(0, 16)}`}
                        ref={
                          isTarget && paragraphIndex === 0
                            ? highlightRef
                            : isTarget
                              ? highlightRef
                              : undefined
                        }
                        className={
                          isTarget
                            ? 'cursor-pointer rounded-r-md border-l-4 border-blue-500 bg-blue-50 px-1.5 py-0.5 text-slate-900'
                            : 'cursor-pointer hover:bg-slate-50'
                        }
                        onClick={() =>
                          updateContext({
                            current_route: '/reading',
                            active_passage_id: activeQuestion.passageId,
                            active_question_id: activeQuestion.id,
                            selected_raw_text: sentence,
                          })
                        }
                        onMouseUp={() => {
                          const selectedText = window.getSelection()?.toString().trim()
                          if (selectedText) {
                            updateContext({
                              current_route: '/reading',
                              active_passage_id: activeQuestion.passageId,
                              active_question_id: activeQuestion.id,
                              selected_raw_text: selectedText,
                            })
                          }
                        }}
                      >
                        {sentence}{' '}
                        {isTarget ? (
                          <span className="ml-1 rounded bg-blue-100 px-1 py-0.5 text-[9px] font-semibold text-blue-700">
                            Q{activeQuestion.number} 定位句
                          </span>
                        ) : null}
                      </span>
                    )
                  })}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm lg:col-span-6 lg:h-full">
          <div className="flex gap-1.5 overflow-x-auto border-b border-slate-200 p-3">
            {currentGroup.questions.map((question) => {
              const attempt = attempts[question.id]
              const active = question.id === activeQuestion.id
              return (
                <button
                  key={question.id}
                  type="button"
                  onClick={() => setActiveQuestionId(question.id)}
                  className={`inline-flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-2 text-[11px] font-medium transition-colors ${
                    active
                      ? 'bg-slate-800 text-white'
                      : 'bg-slate-50 text-slate-500 hover:bg-slate-100 hover:text-slate-800'
                  }`}
                  aria-pressed={active}
                >
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      attempt
                        ? attempt.isCorrect
                          ? 'bg-emerald-400'
                          : 'bg-red-400'
                        : active
                          ? 'bg-slate-400'
                          : 'bg-slate-300'
                    }`}
                  />
                  第 {question.number} 题
                </button>
              )
            })}
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto p-5">
            <div className="flex flex-wrap items-center gap-1.5">
              <Tag tone="violet">{activeQuestion.questionType}</Tag>
              <Tag tone="slate">难度 中等</Tag>
              <Tag tone="slate">建议 6 min</Tag>
              <Tag tone="amber">
                {activeQuestion.answerSource === 'inferred'
                  ? 'AI 推断答案'
                  : activeQuestion.answerSource === 'provided'
                    ? '用户提供答案序列'
                    : activeQuestion.answerSource === 'manual'
                      ? '手工录入答案'
                      : '答案来源未记录'}
              </Tag>
              <Tag tone="slate">
                {activeQuestion.reviewStatus === 'approved' || activeQuestion.reviewStatus === 'reviewed'
                  ? '已人工复核'
                  : activeQuestion.reviewStatus === 'practice'
                    ? '基础练习可用'
                    : '待人工复核'}
              </Tag>
              {isBasicPractice ? <Tag tone="slate">解析待完善</Tag> : null}
            </div>
            <p className="mt-2 text-[11px] leading-relaxed text-amber-700">
              {activeQuestion.answerSourceNote || '答案来源尚未核实；练习判分依据当前保存答案。'}
              {activeQuestion.locationStatus === 'exact_quote'
                ? ' 已匹配唯一原文引句，是否支持答案仍需复核。'
                : ' 原文位置待人工核对；不自动指定第一句或最长句。'}
            </p>

            <h2 className="mt-4 text-[17px] font-semibold leading-relaxed text-slate-900">
              {activeQuestion.content}
            </h2>

            <div className="mt-4 space-y-2.5">
              {optionKeys.map((key) => {
                const analysis = activeQuestion.analysis?.[key]
                const trapType = analysis?.trapType?.trim()
                const tone = trapType ? trapTone(trapType) : 'slate'
                const isSelected = selected === key
                if (!showAnalysis) {
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => setSelected(key)}
                      className={`flex w-full items-start gap-3 rounded-lg border p-4 text-left transition-all ${
                        isSelected
                          ? 'border-slate-800 bg-slate-50 ring-1 ring-slate-900/10'
                          : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                      }`}
                      aria-pressed={isSelected}
                    >
                      <span
                        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-[11px] font-bold ${
                          isSelected
                            ? 'bg-slate-800 text-white'
                            : 'bg-slate-100 text-slate-500'
                        }`}
                      >
                        {key}
                      </span>
                      <span className="text-sm leading-relaxed text-slate-700">
                        {activeQuestion.options[key]}
                      </span>
                    </button>
                  )
                }
                return (
                  <div
                    key={key}
                    className={`rounded-lg border border-slate-200 border-l-4 bg-white p-4 ${borderMap[tone]}`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-slate-100 text-[11px] font-bold text-slate-500">
                        {key}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm leading-relaxed text-slate-700">
                          {activeQuestion.options[key]}
                        </p>
                        <div className="mt-2 flex flex-wrap items-center gap-1.5">
                          {trapType ? <Tag tone={tone}>{trapType}</Tag> : null}
                          {isSelected ? <Tag tone="slate">我的选择</Tag> : null}
                          {key === activeQuestion.correctAnswer ? (
                            <Tag tone="emerald" dot>
                              答案
                            </Tag>
                          ) : null}
                        </div>
                        <p className="mt-2 text-xs leading-relaxed text-slate-500">
                          {analysis?.explanation?.trim() || '本选项解析待完善。'}
                        </p>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            {showAnalysis ? (
              <div
                className={`mt-4 flex items-start gap-2.5 rounded-lg px-3.5 py-3 ${
                  currentAttempt?.isCorrect
                    ? 'bg-emerald-50 text-emerald-800'
                    : 'bg-red-50 text-red-800'
                }`}
                role="status"
              >
                {currentAttempt?.isCorrect ? (
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                ) : (
                  <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
                )}
                <div>
                  <p className="text-xs font-semibold">
                    {currentAttempt?.isCorrect
                      ? '回答正确'
                      : `回答错误，正确答案是 ${activeQuestion.correctAnswer}`}
                  </p>
                  <p className="mt-0.5 text-[11px] opacity-80">
                    你的答案 {currentAttempt?.answer} · 已记录
                  </p>
                </div>
              </div>
            ) : null}

            {showAnalysis ? (
              <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50/60 p-4">
                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
                  解题路径
                </p>
                <div className="mt-2 space-y-1.5">
                  {steps.length === 0 ? (
                    <p className="text-[11px] leading-relaxed text-slate-500">
                      解题步骤待完善，当前可依据已保存答案进行练习和判分。
                    </p>
                  ) : steps.slice(0, 6).map((step, index) => (
                    <div
                      key={step}
                      className="flex items-start gap-2 text-[11px] leading-relaxed text-slate-600"
                    >
                      <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded bg-white text-[9px] font-bold text-slate-400 ring-1 ring-slate-200">
                        {index + 1}
                      </span>
                      {step}
                    </div>
                  ))}
                </div>
              </div>
            ) : null}

            {agentError ? (
              <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-[11px] leading-relaxed text-amber-800">
                后端未连接，答案只保存在本地。
              </p>
            ) : null}

            {agentFeedback ? (
              <div className="mt-4 space-y-3">
                <ToolTrace
                  tools={agentFeedback.tool_trace}
                  title="本次诊断工具链"
                />
                <CitationList citations={agentFeedback.citations} compact />
              </div>
            ) : null}
            {trapCard ? (
              <TrapMethodCardView
                card={trapCard}
                hitCount={learnerProfile?.trap_counts[trapCard.name]}
              />
            ) : null}
          </div>

          <div className="border-t border-slate-200 p-4">
            <div className="flex items-center justify-between gap-3">
              <span className="text-[11px] text-slate-400">
                {showAnalysis
                  ? '已提交'
                  : selected
                    ? `已选择 ${selected}`
                    : '请选择答案'}
              </span>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!selected || showAnalysis}
                className="inline-flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2.5 text-xs font-semibold text-white transition-colors hover:bg-slate-900 disabled:bg-slate-200 disabled:text-slate-400"
              >
                {showAnalysis ? '已提交' : '提交答案'}
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </section>
      </div>

      {context.selected_raw_text ? (
        <div className="fixed bottom-6 left-1/2 z-30 flex -translate-x-1/2 items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-2.5 py-2 shadow-xl shadow-slate-900/10">
          <span className="max-w-[260px] truncate px-1 text-[10px] text-slate-500">
            已捕获：{context.selected_raw_text}
          </span>
          <button
            type="button"
            onClick={() => void sendMessage(`请用五步法拆解这句：${context.selected_raw_text}`)}
            className="rounded-md bg-slate-900 px-2 py-1.5 text-[10px] font-medium text-white hover:bg-slate-800"
          >
            五步拆解
          </button>
          <button
            type="button"
            onClick={() => void sendMessage(`请查这句里的熟词僻义：${context.selected_raw_text}`)}
            className="rounded-md border border-slate-200 bg-white px-2 py-1.5 text-[10px] font-medium text-slate-600 hover:bg-slate-50"
          >
            查熟词僻义
          </button>
          <button
            type="button"
            onClick={() => {
              document.querySelector<HTMLTextAreaElement>('[data-agent-input]')?.focus()
            }}
            className="rounded-md border border-slate-200 bg-white px-2 py-1.5 text-[10px] font-medium text-slate-600 hover:bg-slate-50"
          >
            问 Agent
          </button>
          <button
            type="button"
            onClick={() => updateContext({ selected_raw_text: null })}
            aria-label="清除划选"
            className="flex h-7 w-7 items-center justify-center rounded-md text-slate-400 hover:bg-slate-100"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      ) : null}

      {summary ? (
        <div className="fixed inset-0 z-[75] flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-[2px]">
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-5 shadow-2xl">
            <div className="flex items-center justify-between gap-2">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
                  训练结束
                </p>
                <h2 className="mt-1 text-lg font-bold text-slate-900">本次阅读 session</h2>
              </div>
              <button type="button" onClick={() => setSummary(null)} className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100" aria-label="关闭">✕</button>
            </div>
            <div className="mt-4 grid grid-cols-3 gap-2">
              <div className="rounded-lg bg-slate-50 p-3 text-center">
                <p className="text-xl font-bold tabular-nums text-slate-900">
                  {String(Math.floor(summary.duration / 60)).padStart(2, '0')}:{String(summary.duration % 60).padStart(2, '0')}
                </p>
                <p className="mt-1 text-[9px] text-slate-400">用时</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-3 text-center">
                <p className="text-xl font-bold tabular-nums text-slate-900">{summary.answered}/{summary.total}</p>
                <p className="mt-1 text-[9px] text-slate-400">已答</p>
              </div>
              <div className="rounded-lg bg-slate-50 p-3 text-center">
                <p className="text-xl font-bold tabular-nums text-emerald-600">{Math.round((summary.correct / Math.max(1, summary.answered)) * 100)}%</p>
                <p className="mt-1 text-[9px] text-slate-400">正确率</p>
              </div>
            </div>
            <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-[10px] leading-5 text-amber-800">
              错题诊断已触发，本次 session 已写入 SQLite。把本篇生词收进词本后，今日路径会自动更新。
            </p>
            <div className="mt-3 grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  void sendMessage('把这篇阅读里的生词整理入库。')
                  setSummary(null)
                }}
                className="rounded-lg bg-slate-900 px-3 py-2 text-[11px] font-semibold text-white hover:bg-slate-800"
              >
                提取本篇生词
              </button>
              <button
                type="button"
                onClick={() => setSummary(null)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-[11px] font-medium text-slate-600 hover:bg-slate-50"
              >
                继续看题
              </button>
            </div>
          </div>
        </div>
      ) : null}

    </div>
  )
}
