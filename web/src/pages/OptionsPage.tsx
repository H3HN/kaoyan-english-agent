import { useMemo, useState } from 'react'
import {
  ArrowRight,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Lightbulb,
  MapPin,
  Target,
  XCircle,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { PageHero } from '../components/PageHero'
import { CitationList, ToolTrace } from '../components/ToolTrace'
import { SectionHeader } from '../components/SectionHeader'
import { Tag, toneStyles, type Tone } from '../components/Tag'
import { getPassage, questions, type OptionKey } from '../data/content'
import { api, type OptionWorkflow } from '../lib/api'
import { useAppStore } from '../store/AppStore'

const optionKeys: OptionKey[] = ['A', 'B', 'C', 'D']

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

export default function OptionsPage() {
  const [activeId, setActiveId] = useState(questions[0].id)
  const [selected, setSelected] = useState<OptionKey | null>(null)
  const [submitted, setSubmitted] = useState<{
    isCorrect: boolean
    answer: OptionKey
  } | null>(null)
  const [showPassage, setShowPassage] = useState(false)
  const [agentFeedback, setAgentFeedback] = useState<OptionWorkflow | null>(null)
  const [agentError, setAgentError] = useState(false)
  const { addRecord } = useAppStore()

  const question = questions.find((item) => item.id === activeId) ?? questions[0]
  const passage = getPassage(question.passageId)
  const questionIndex = useMemo(
    () => questions.findIndex((item) => item.id === question.id),
    [question.id],
  )

  const handleSelectQuestion = (id: string) => {
    setActiveId(id)
    setSelected(null)
    setSubmitted(null)
    setShowPassage(false)
    setAgentFeedback(null)
    setAgentError(false)
  }

  const handleSubmit = () => {
    if (!selected) return
    const record = addRecord({
      questionId: question.id,
      questionType: question.questionType,
      userAnswer: selected,
      correctAnswer: question.correctAnswer,
    })
    setSubmitted({ isCorrect: record.isCorrect, answer: selected })
    setAgentFeedback(null)
    setAgentError(false)
    api
      .runOptions(question.id, selected)
      .then(setAgentFeedback)
      .catch(() => setAgentError(true))
  }

  return (
    <div className="space-y-6">
      <PageHero
        eyebrow="OPTION LAB"
        title="选项陷阱分析"
        subtitle="左边回到原文，右边拆开四个选项。先识别题型，再定位依据，最后用陷阱类型完成排除。"
        actions={
          <span className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-medium text-white">
            <Target className="h-4 w-4" />
            第 {questionIndex + 1} / {questions.length} 题
          </span>
        }
      />

      <div className="flex flex-wrap items-center gap-2 rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
        <span className="px-1 text-[11px] font-medium text-slate-400">
          真题选择
        </span>
        {questions.map((item) => {
          const isActive = item.id === question.id
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => handleSelectQuestion(item.id)}
              className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition-colors ${
                isActive
                  ? 'bg-slate-800 text-white'
                  : 'bg-slate-50 text-slate-500 hover:bg-slate-100 hover:text-slate-800'
              }`}
              aria-pressed={isActive}
            >
              {item.year} {item.examType} · Text {item.textNumber}
              <span className={isActive ? 'text-slate-400' : 'text-slate-400'}>
                Q{item.number}
              </span>
            </button>
          )
        })}
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
        <div className="lg:sticky lg:top-24 lg:self-start">
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-100 bg-slate-50/60 px-5 py-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Tag tone="violet">{question.questionType}</Tag>
                  <span className="text-[11px] text-slate-400">
                    {question.year} {question.examType} · Text{' '}
                    {question.textNumber} · 第 {question.number} 题
                  </span>
                </div>
                <span className="text-[11px] text-slate-400">题干</span>
              </div>
            </div>

            <div className="px-5 py-6 sm:px-6">
              <h2 className="text-balance text-[17px] font-semibold leading-relaxed text-slate-900">
                {question.content}
              </h2>

              <div className="mt-6">
                <div className="flex items-center gap-2">
                  <MapPin className="h-3.5 w-3.5 text-blue-500" />
                  <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                    原文定位
                  </span>
                  <span className="ml-auto text-[11px] text-slate-400">
                    {question.location}
                  </span>
                </div>
                <div className="relative mt-3 overflow-hidden rounded-lg border border-slate-200 bg-slate-50/70 p-4">
                  <span className="absolute inset-y-0 left-0 w-1 bg-blue-500" />
                  <p className="font-serif text-[14.5px] leading-8 text-slate-800">
                    {question.sourceSentence}
                  </p>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {question.sourceHighlights.map((keyword) => (
                    <Tag key={keyword} tone="cyan">
                      {keyword}
                    </Tag>
                  ))}
                </div>
              </div>

              <button
                type="button"
                onClick={() => setShowPassage((value) => !value)}
                className="mt-5 flex w-full items-center justify-between rounded-lg border border-slate-200 px-3.5 py-2.5 text-xs font-medium text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-800"
                aria-expanded={showPassage}
              >
                <span>{showPassage ? '收起全文' : '展开全文'}</span>
                <ChevronDown
                  className={`h-4 w-4 transition-transform ${
                    showPassage ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {showPassage ? (
                <div className="mt-3 rounded-lg border border-slate-200 bg-white p-4">
                  <p className="font-serif text-[13.5px] leading-7 text-slate-600">
                    {passage?.passage}
                  </p>
                </div>
              ) : null}

              <div className="mt-5 flex items-start gap-2 rounded-lg bg-blue-50/70 px-3.5 py-3">
                <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0 text-blue-500" />
                <p className="text-[11px] leading-relaxed text-blue-900/70">
                  先自己定位，再对照右侧分析。不要把“看起来像原文”的选项当成同义替换。
                </p>
              </div>
            </div>
          </div>

          <div className="mt-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-900">本题信息</h3>
              <Tag tone="slate">阅读 · {question.questionType}</Tag>
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3">
              <div>
                <dt className="text-[10px] text-slate-400">真题来源</dt>
                <dd className="mt-1 text-[11px] font-medium text-slate-600">
                  {question.year} {question.examType} · Text {question.textNumber}
                </dd>
              </div>
              <div>
                <dt className="text-[10px] text-slate-400">建议用时</dt>
                <dd className="mt-1 text-[11px] font-medium text-slate-600">
                  6 分钟
                </dd>
              </div>
              <div>
                <dt className="text-[10px] text-slate-400">定位范围</dt>
                <dd className="mt-1 text-[11px] font-medium text-slate-600">
                  全文
                </dd>
              </div>
              <div>
                <dt className="text-[10px] text-slate-400">难度</dt>
                <dd className="mt-1 text-[11px] font-medium text-slate-600">
                  中等
                </dd>
              </div>
            </dl>
            <Link
              to="/knowledge"
              className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-[11px] font-medium text-slate-500 transition-colors hover:text-slate-800"
            >
              查看{question.questionType}方法论
              <ChevronRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>

        <div>
          <SectionHeader
            title="四个选项，逐一验伪"
            description="点击卡片标记你的答案，再提交查看结果。"
            action={
              <span className="text-[11px] text-slate-400">
                {question.correctAnswer} 为正确项
              </span>
            }
          />

          <div className="space-y-3">
            {optionKeys.map((key) => {
              const analysis = question.analysis[key]
              const tone = trapTone(analysis.trapType)
              const isSelected = selected === key
              return (
                <button
                  key={key}
                  type="button"
                  onClick={() => {
                    if (selected !== key) setSubmitted(null)
                    setSelected(key)
                  }}
                  className={`group relative w-full overflow-hidden rounded-xl border border-l-4 bg-white p-4 text-left shadow-sm transition-all duration-200 ${borderMap[tone]} ${
                    isSelected
                      ? 'border-slate-300 ring-2 ring-slate-900/10'
                      : 'border-slate-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md'
                  }`}
                  aria-pressed={isSelected}
                >
                  <div className="flex items-start gap-3">
                    <span
                      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-xs font-bold ${toneStyles[tone].soft} ${toneStyles[tone].text}`}
                    >
                      {key}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm leading-relaxed text-slate-800">
                        {question.options[key]}
                      </p>
                      <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
                        <Tag tone={tone}>{analysis.trapType}</Tag>
                        {isSelected ? <Tag tone="slate">我的选择</Tag> : null}
                        {key === question.correctAnswer ? (
                          <Tag tone="emerald" dot>
                            答案
                          </Tag>
                        ) : null}
                      </div>
                      <p className="mt-2 text-xs leading-relaxed text-slate-500">
                        {analysis.explanation}
                      </p>
                    </div>
                  </div>
                </button>
              )
            })}
          </div>

          <div className="mt-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            {submitted ? (
              <div
                className={`mb-3 flex items-start gap-2.5 rounded-lg px-3.5 py-3 ${
                  submitted.isCorrect
                    ? 'bg-emerald-50 text-emerald-800'
                    : 'bg-red-50 text-red-800'
                }`}
                role="status"
              >
                {submitted.isCorrect ? (
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                ) : (
                  <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
                )}
                <div>
                  <p className="text-xs font-semibold">
                    {submitted.isCorrect
                      ? '回答正确'
                      : `回答错误，正确答案是 ${question.correctAnswer}`}
                  </p>
                  <p className="mt-0.5 text-[11px] opacity-80">
                    你的答案 {submitted.answer} · 已同步到学习报告
                  </p>
                </div>
              </div>
            ) : null}
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-[11px] text-slate-400">
                {selected
                  ? `已选择 ${selected}，确认后提交`
                  : '请选择一个答案后提交'}
              </p>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!selected || Boolean(submitted)}
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-800 px-4 py-2.5 text-xs font-semibold text-white transition-colors hover:bg-slate-900 disabled:bg-slate-200 disabled:text-slate-400"
              >
                {submitted ? '已提交' : '提交答案'}
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>

          {agentError ? (
            <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-[11px] leading-relaxed text-amber-800">
              后端未连接，答案只保存在本地；启动 FastAPI 后可自动记录陷阱类型并返回真题出处。
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
        </div>
      </div>

      <section>
        <SectionHeader
          title="解题路径"
          description="从题干到答案，固定成一条可复用的检查链。"
        />
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="grid gap-3 md:grid-cols-5">
            {question.steps.map((step, index) => (
              <div
                key={step}
                className="relative rounded-lg border border-slate-200 bg-slate-50/60 p-3.5"
              >
                <span className="flex h-6 w-6 items-center justify-center rounded-md bg-white text-[10px] font-bold text-slate-500 ring-1 ring-slate-200">
                  {index + 1}
                </span>
                <p className="mt-2.5 text-[11px] leading-relaxed text-slate-600">
                  {step}
                </p>
                {index < question.steps.length - 1 ? (
                  <span className="absolute -right-2 top-1/2 hidden h-px w-4 bg-slate-200 md:block" />
                ) : null}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
