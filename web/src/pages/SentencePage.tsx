import { useEffect, useMemo, useState } from 'react'
import {
  ArrowRight,
  BookOpenCheck,
  Braces,
  ChevronRight,
  Database,
  GitBranch,
  Languages,
  Lightbulb,
  Link2,
  Loader2,
  Network,
  Plus,
  Quote,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { PageHero } from '../components/PageHero'
import { ProgressBar } from '../components/ProgressBar'
import { SectionHeader } from '../components/SectionHeader'
import { Tag, toneStyles } from '../components/Tag'
import { CitationList, ToolTrace } from '../components/ToolTrace'
import { useToast } from '../components/Toast'
import type { TreeNode } from '../data/content'
import {
  api,
  type PassageSentence,
  type PassageSummary,
  type SentenceBreakdown,
  type SentenceWorkflow,
  type VocabEntry,
} from '../lib/api'
import { useAppStore } from '../store/AppStore'

const STEP_LABELS = [
  { title: '找主干', icon: Braces },
  { title: '剥离从句', icon: GitBranch },
  { title: '划分修饰', icon: Link2 },
  { title: '逐层翻译', icon: Languages },
  { title: '标注语法点', icon: Lightbulb },
]

function TreeNodeView({ node, depth = 0 }: { node: TreeNode; depth?: number }) {
  return (
    <div className={depth > 0 ? 'relative pl-4' : 'relative'}>
      {depth > 0 ? (
        <span className="absolute left-0 top-0 h-full w-px bg-slate-200" />
      ) : null}
      <div className="relative flex flex-col gap-1 py-1.5 sm:flex-row sm:items-baseline sm:gap-2">
        {depth > 0 ? (
          <span className="absolute -left-4 top-4 h-px w-3 bg-slate-200" />
        ) : null}
        <span className="shrink-0">
          <Tag tone={depth === 0 ? 'blue' : 'slate'}>{node.role}</Tag>
        </span>
        <span className="font-serif text-[13.5px] leading-relaxed text-slate-700">
          {node.label}
        </span>
      </div>
      {node.children?.length ? (
        <div className="ml-2 border-l border-slate-200 pl-3">
          {node.children.map((child, index) => (
            <TreeNodeView
              key={`${child.label}-${index}`}
              node={child}
              depth={depth + 1}
            />
          ))}
        </div>
      ) : null}
    </div>
  )
}

export default function SentencePage() {
  const [passages, setPassages] = useState<PassageSummary[]>([])
  const [passagesStatus, setPassagesStatus] = useState<'loading' | 'ready' | 'error'>('loading')
  const [sentencesStatus, setSentencesStatus] = useState<'loading' | 'ready' | 'error'>('loading')
  const [passageId, setPassageId] = useState('')
  const [sentences, setSentences] = useState<PassageSentence[]>([])
  const [sentenceId, setSentenceId] = useState('')
  const [breakdown, setBreakdown] = useState<SentenceBreakdown | null>(null)
  const [breakdownStatus, setBreakdownStatus] = useState<
    'loading' | 'ready' | 'error'
  >('loading')
  const [activeStep, setActiveStep] = useState(0)
  const [agentData, setAgentData] = useState<SentenceWorkflow | null>(null)
  const [agentStatus, setAgentStatus] = useState<'loading' | 'ready' | 'error'>(
    'loading',
  )
  const { addWord } = useAppStore()
  const toast = useToast()

  useEffect(() => {
    let alive = true
    api
      .getPassages()
      .then((response) => {
        if (!alive) return
        setPassages(response.items)
        setPassageId(response.items[0]?.id ?? '')
        setPassagesStatus('ready')
      })
      .catch(() => {
        if (alive) {
          setPassages([])
          setPassageId('')
          setPassagesStatus('error')
        }
      })
    return () => {
      alive = false
    }
  }, [])

  useEffect(() => {
    if (!passageId) return
    let alive = true
    setSentences([])
    setSentencesStatus('loading')
    setSentenceId('')
    setBreakdown(null)
    setActiveStep(0)
    api
      .getPassageSentences(passageId)
      .then((response) => {
        if (!alive) return
        setSentences(response.items)
        setSentencesStatus('ready')
        const longest = response.items.reduce<PassageSentence | null>(
          (best, item) =>
            !best || item.word_count > best.word_count ? item : best,
          null,
        )
        const first = longest ?? response.items[0]
        if (first) setSentenceId(first.id)
      })
      .catch(() => {
        if (alive) setSentencesStatus('error')
      })
    return () => {
      alive = false
    }
  }, [passageId])

  useEffect(() => {
    if (!sentenceId) return
    let alive = true
    setBreakdown(null)
    setBreakdownStatus('loading')
    setActiveStep(0)
    api
      .getSentenceBreakdown(sentenceId)
      .then((data) => {
        if (!alive) return
        setBreakdown(data)
        setBreakdownStatus('ready')
      })
      .catch(() => {
        if (!alive) return
        setBreakdownStatus('error')
      })
    return () => {
      alive = false
    }
  }, [sentenceId])

  useEffect(() => {
    if (!sentenceId) return
    let alive = true
    setAgentStatus('loading')
    setAgentData(null)
    api
      .runSentence(sentenceId)
      .then((data) => {
        if (!alive) return
        setAgentData(data)
        setAgentStatus('ready')
      })
      .catch(() => {
        if (!alive) return
        setAgentStatus('error')
      })
    return () => {
      alive = false
    }
  }, [sentenceId])

  const currentPassage = passages.find((item) => item.id === passageId)
  const currentSentence = sentences.find((item) => item.id === sentenceId)
  const placeholder: SentenceBreakdown = {
    id: sentenceId,
    index: currentSentence?.index ?? 1,
    source: currentSentence?.source ?? '',
    original: currentSentence?.text ?? '',
    wordCount: currentSentence?.word_count ?? 0,
    isLong: currentSentence?.is_long ?? false,
    main: currentSentence?.text ?? '正在读取句子…',
    mainNote:
      breakdownStatus === 'loading'
        ? '正在请求 DeepSeek 生成五步拆解，首次约 5–10 秒。'
        : '当前未能生成拆解，请稍后重试。',
    clauseNote: '',
    clauses: [],
    modifiers: [],
    translation: '',
    translationLayers: [],
    grammar: [],
    examPoints: [],
    tree: currentSentence
      ? [{ role: '整句', label: currentSentence.text }]
      : [],
    segments: currentSentence
      ? [{ text: currentSentence.text, tone: 'slate' }]
      : [],
    llmUsed: false,
  }
  const analysis = breakdown ?? placeholder
  const wordCount = analysis.wordCount || currentSentence?.word_count || 0
  const legendItems = useMemo(() => {
    const map = new Map<string, string>()
    analysis.segments.forEach((segment) => {
      if (segment.label) map.set(segment.label, segment.tone)
    })
    return Array.from(map.entries())
  }, [analysis.segments])
  const treeNodes = analysis.tree.length
    ? analysis.tree
    : [{ role: '整句', label: analysis.original }]

  const handleArchiveWord = (entry: VocabEntry) => {
    const result = addWord({
      spelling: entry.word,
      meaning: entry.basic_meaning || entry.rare_meaning || entry.word,
      source: analysis.source,
      context: analysis.original,
    })
    toast(result.message, result.ok ? 'success' : 'info')
  }

  if (!currentPassage || !currentSentence || sentencesStatus !== 'ready') {
    const loading = passagesStatus === 'loading' ||
      (Boolean(currentPassage) && sentencesStatus === 'loading')
    const error = passagesStatus === 'error' ||
      (Boolean(currentPassage) && sentencesStatus === 'error')
    return (
      <div className="space-y-6">
        <PageHero eyebrow="SENTENCE STUDIO" title="长难句拆解" />
        {passages.length > 0 ? (
          <select
            value={passageId}
            onChange={(event) => setPassageId(event.target.value)}
            aria-label="选择文章"
            className="h-9 max-w-full rounded-lg border border-slate-200 bg-white px-3 text-xs font-medium text-slate-700 outline-none"
          >
            {passages.map((item) => (
              <option key={item.id} value={item.id}>
                {item.year} {item.exam_type} · Text {item.text_number}
              </option>
            ))}
          </select>
        ) : null}
        <div
          role="status"
          className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white p-8 text-sm text-slate-500"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin text-slate-400" />
              正在读取学习篇章…
            </>
          ) : error ? (
            '无法读取学习内容，请稍后重试。'
          ) : currentPassage ? (
            '该篇章暂无可学习的句子。'
          ) : (
            '暂无已发布的真题篇章，发布后即可开始学习。'
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHero
        eyebrow="SENTENCE STUDIO"
        title="长难句拆解"
        actions={
          <Link
            to="/options"
            className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-white/10"
          >
            去做选项分析
            <ArrowRight className="h-4 w-4" />
          </Link>
        }
      />

      <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-medium text-slate-400">文章</span>
          <select
            value={passageId}
            onChange={(event) => setPassageId(event.target.value)}
            aria-label="选择文章"
            className="h-9 max-w-[280px] rounded-lg border border-slate-200 bg-white px-3 text-xs font-medium text-slate-700 outline-none"
          >
            {passages.map((item) => (
              <option key={item.id} value={item.id}>
                {item.year} {item.exam_type} · Text {item.text_number}
              </option>
            ))}
          </select>

          <span className="ml-2 text-[11px] font-medium text-slate-400">
            句子
          </span>
          <select
            value={sentenceId}
            onChange={(event) => {
              setSentenceId(event.target.value)
              setActiveStep(0)
            }}
            aria-label="选择句子"
            className="h-9 max-w-[320px] rounded-lg border border-slate-200 bg-white px-3 text-xs font-medium text-slate-700 outline-none"
          >
            {sentences.map((item) => (
              <option key={item.id} value={item.id}>
                第 {item.index} 句 · {item.word_count} 词
                {item.is_long ? ' · 长难句' : ''}
              </option>
            ))}
          </select>

          {breakdownStatus === 'loading' ? (
            <span className="inline-flex items-center gap-1.5 text-[11px] text-slate-400">
              <Loader2 className="h-3 w-3 animate-spin" />
              正在生成拆解
            </span>
          ) : null}
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <Tag tone="blue">
              {currentPassage?.year} {currentPassage?.exam_type}
            </Tag>
            <span className="text-[11px] text-slate-400">
              Text {currentPassage?.text_number} · {currentPassage?.question_count}{' '}
              题 · {sentences.length} 句
            </span>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-slate-400">
            <span>{wordCount} 词</span>
            {analysis.llmUsed ? <Tag tone="violet">DeepSeek 拆解</Tag> : null}
          </div>
        </div>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-5">
          <div className="flex items-center gap-2">
            <Tag tone={analysis.isLong ? 'amber' : 'emerald'} dot>
              {analysis.isLong ? '长难句' : '简单句'}
            </Tag>
            <span className="text-[11px] text-slate-400">{analysis.source}</span>
          </div>
        </div>

        <div className="py-7">
          <p className="whitespace-pre-wrap font-serif text-[20px] leading-[1.95] tracking-[-0.01em] text-slate-900 sm:text-[23px]">
            {analysis.segments.map((segment, index) => {
              const styles = toneStyles[segment.tone as keyof typeof toneStyles]
              const plain = segment.tone === 'slate'
              return (
                <span
                  key={`${segment.text}-${index}`}
                  title={segment.label}
                  className={
                    plain
                      ? ''
                      : `${styles.soft} rounded-md px-1 py-0.5 text-slate-900`
                  }
                >
                  {segment.text}
                </span>
              )
            })}
          </p>
          {legendItems.length > 0 ? (
            <div className="mt-4 flex flex-wrap items-center gap-2">
              <span className="text-[10px] font-medium uppercase tracking-[0.14em] text-slate-400">
                结构标记
              </span>
              {legendItems.map(([label, tone]) => (
                <Tag key={label} tone={tone as keyof typeof toneStyles} dot>
                  {label}
                </Tag>
              ))}
            </div>
          ) : null}
        </div>

        <div className="border-t border-slate-100 pt-6">
          <div className="relative">
            <div className="absolute left-0 right-0 top-4 hidden h-px bg-slate-200 sm:block" />
            <div className="relative grid grid-cols-5 gap-2">
              {STEP_LABELS.map((step, index) => {
                const Icon = step.icon
                const isActive = index === activeStep
                return (
                  <button
                    key={step.title}
                    type="button"
                    onClick={() => setActiveStep(index)}
                    className="group flex flex-col items-center gap-2 text-center"
                    aria-current={isActive ? 'step' : undefined}
                  >
                    <span
                      className={`relative z-10 flex h-8 w-8 items-center justify-center rounded-full border text-[11px] font-semibold transition-all ${
                        isActive
                          ? 'border-slate-800 bg-slate-800 text-white shadow-sm'
                          : 'border-slate-200 bg-white text-slate-400 group-hover:border-slate-300 group-hover:text-slate-600'
                      }`}
                    >
                      {isActive ? (
                        <span>{index + 1}</span>
                      ) : (
                        <Icon className="h-3.5 w-3.5" />
                      )}
                    </span>
                    <span
                      className={`text-[11px] leading-tight ${
                        isActive
                          ? 'font-semibold text-slate-900'
                          : 'font-medium text-slate-400 group-hover:text-slate-600'
                      }`}
                    >
                      {index + 1}. {step.title}
                    </span>
                  </button>
                )
              })}
            </div>
          </div>

          <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50/70 p-4 sm:p-5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-semibold text-slate-900">
                第 {activeStep + 1} 步 · {STEP_LABELS[activeStep].title}
              </h3>
            </div>

            {activeStep === 0 ? (
              <div className="mt-4">
                <p className="font-serif text-[15px] leading-relaxed text-slate-800">
                  {analysis.main}
                </p>
                <p className="mt-3 text-xs leading-relaxed text-slate-500">
                  {analysis.mainNote}
                </p>
              </div>
            ) : null}

            {activeStep === 1 ? (
              <div className="mt-4 space-y-3">
                <p className="text-xs leading-relaxed text-slate-500">
                  {analysis.clauseNote}
                </p>
                {analysis.clauses.length > 0 ? (
                  analysis.clauses.map((clause) => (
                    <div
                      key={clause.text}
                      className="rounded-lg border border-slate-200 bg-white p-3.5"
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <Tag tone="violet">{clause.label}</Tag>
                        <span className="text-[11px] text-slate-400">
                          {clause.note}
                        </span>
                      </div>
                      <p className="mt-2 font-serif text-sm leading-relaxed text-slate-800">
                        {clause.text}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="rounded-lg border border-dashed border-slate-200 bg-white px-4 py-5 text-center text-xs text-slate-400">
                    当前拆解未标注独立从句，可结合主干与修饰成分查看。
                  </div>
                )}
              </div>
            ) : null}

            {activeStep === 2 ? (
              <div className="mt-4 space-y-2.5">
                {analysis.modifiers.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-slate-200 bg-white px-4 py-5 text-center text-xs text-slate-400">
                    当前拆解未标注额外修饰成分。
                  </div>
                ) : null}
                {analysis.modifiers.map((modifier) => (
                  <div
                    key={modifier.text}
                    className="flex flex-col gap-1.5 rounded-lg border border-slate-200 bg-white px-4 py-3 sm:flex-row sm:items-start sm:gap-3"
                  >
                    <Tag tone="amber" className="shrink-0">
                      {modifier.label}
                    </Tag>
                    <div className="min-w-0">
                      <p className="font-serif text-sm leading-relaxed text-slate-800">
                        {modifier.text}
                      </p>
                      <p className="mt-1 text-[11px] leading-relaxed text-slate-400">
                        {modifier.note}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : null}

            {activeStep === 3 ? (
              <div className="mt-4 space-y-2">
                {(analysis.translationLayers.length
                  ? analysis.translationLayers
                  : analysis.translation
                    ? [analysis.translation]
                    : []
                ).map((layer, index) => (
                  <div key={layer} className="flex items-center gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-white text-[10px] font-semibold text-slate-400 ring-1 ring-slate-200">
                      {index + 1}
                    </span>
                    <p className="flex-1 rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-xs leading-relaxed text-slate-700">
                      {layer}
                    </p>
                  </div>
                ))}
              </div>
            ) : null}

            {activeStep === 4 ? (
              <div className="mt-4 grid gap-4 lg:grid-cols-2">
                <div className="space-y-2">
                  {analysis.grammar.length === 0 ? (
                  <div className="rounded-lg border border-dashed border-slate-200 bg-white px-4 py-5 text-center text-xs text-slate-400">
                    当前拆解未标注独立语法点。
                  </div>
                ) : null}
                {analysis.grammar.map((point) => (
                    <div
                      key={point.name}
                      className="rounded-lg border border-slate-200 bg-white px-3.5 py-3"
                    >
                      <p className="text-xs font-semibold text-slate-800">
                        {point.name}
                      </p>
                      <p className="mt-1 text-[11px] leading-relaxed text-slate-400">
                        {point.note}
                      </p>
                    </div>
                  ))}
                </div>
                <div className="rounded-lg border border-amber-100 bg-amber-50/70 px-4 py-3.5">
                  <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-amber-700">
                    名师考点
                  </p>
                  <ul className="mt-2.5 space-y-2">
                    {(analysis.examPoints.length
                      ? analysis.examPoints
                      : ['先找谓语，再判断从句修饰对象。']
                    ).map((point) => (
                      <li
                        key={point}
                        className="flex items-start gap-2 text-[11px] leading-relaxed text-amber-900/80"
                      >
                        <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-amber-500" />
                        {point}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </section>


      <section>
        <SectionHeader
          title="Agent 工具链"
          action={
            <span className="inline-flex items-center gap-1.5 text-[11px] text-slate-400">
              <Database className="h-3.5 w-3.5" />
              SQLite · FastAPI
            </span>
          }
        />

        {agentStatus === 'loading' ? (
          <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-5 py-6 shadow-sm">
            <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
            <div>
              <p className="text-xs font-semibold text-slate-800">
                正在调用大纲词库与真题检索…
              </p>
              <p className="mt-0.5 text-[11px] text-slate-400">
                check_syllabus_vocab → search_past_exams
              </p>
            </div>
          </div>
        ) : null}

        {agentStatus === 'error' ? (
          <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 text-xs leading-relaxed text-amber-800">
            当前无法获取词库核验与真题溯源，请稍后重试。
          </div>
        ) : null}

        {agentStatus === 'ready' && agentData ? (
          <div className="space-y-4">
            <ToolTrace tools={agentData.tool_trace} title="本次执行记录" />
            <div className="grid gap-4 lg:grid-cols-3">
              <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm lg:col-span-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-50">
                      <Database className="h-3.5 w-3.5 text-cyan-600" />
                    </span>
                    <h3 className="text-xs font-semibold text-slate-900">
                      大纲词核验
                    </h3>
                  </div>
                  <span className="text-[10px] text-slate-400">
                    命中 {agentData.vocabulary_all_count} 个大纲词 · 展示前{' '}
                    {agentData.vocabulary.length} 个
                  </span>
                </div>
                <div className="mt-3 grid gap-2 sm:grid-cols-2">
                  {agentData.vocabulary.map((entry) => (
                    <div
                      key={entry.word}
                      className="rounded-lg border border-slate-100 bg-slate-50/60 p-3"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-serif text-sm font-semibold text-slate-900">
                          {entry.word}
                        </span>
                        <Tag
                          tone={entry.level === '核心' ? 'emerald' : 'slate'}
                        >
                          {entry.level}
                        </Tag>
                      </div>
                      <p className="mt-1 line-clamp-2 text-[10px] leading-relaxed text-slate-500">
                        {entry.basic_meaning}
                      </p>
                      {entry.rare_meaning ? (
                        <p className="mt-1.5 rounded-md bg-amber-50 px-2 py-1 text-[10px] leading-relaxed text-amber-800">
                          熟词僻义：{entry.rare_meaning}
                        </p>
                      ) : null}
                      <div className="mt-2 flex items-center justify-between gap-2">
                        <span className="text-[9px] text-slate-400">
                          切片频次 {entry.exam_frequency}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleArchiveWord(entry)}
                          className="inline-flex items-center gap-1 rounded-md px-1.5 py-1 text-[10px] font-medium text-slate-500 transition-colors hover:bg-white hover:text-slate-800"
                        >
                          <Plus className="h-3 w-3" />
                          单词本
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <CitationList citations={agentData.citations} />
            </div>
          </div>
        ) : null}
      </section>

      <div className="grid gap-6 lg:grid-cols-12">
        <div className="lg:col-span-7">
          <SectionHeader
            title="语法成分剥离"
            action={
              <span className="inline-flex items-center gap-1.5 text-[11px] text-slate-400">
                <Network className="h-3.5 w-3.5" />
                语法树
              </span>
            }
          />
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
            <div className="mb-4 flex items-center gap-2 border-b border-slate-100 pb-3">
              <GitBranch className="h-4 w-4 text-slate-400" />
              <span className="text-xs font-medium text-slate-500">
                {analysis.source}
              </span>
            </div>
            <div className="space-y-2">
              {treeNodes.map((node, index) => (
                <TreeNodeView key={`${node.label}-${index}`} node={node} />
              ))}
            </div>
          </div>
        </div>

        <div className="space-y-6 lg:col-span-5">
          <div>
            <SectionHeader title="规范译文" />
            <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <span className="absolute inset-y-0 left-0 w-1 bg-blue-500" />
              <Quote className="h-4 w-4 text-blue-200" />
              <p className="mt-2 text-sm leading-8 text-slate-700">
                {analysis.translation || '当前未生成译文。'}
              </p>
            </div>
          </div>

          <div>
            <SectionHeader title="名师考点" />
            <div className="relative overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <span className="absolute inset-y-0 left-0 w-1 bg-amber-500" />
              <div className="space-y-3">
                {(analysis.examPoints.length
                  ? analysis.examPoints
                  : ['先找谓语，再判断从句修饰对象。']
                ).map((point, index) => (
                  <div key={point} className="flex items-start gap-3">
                    <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-amber-50 text-[10px] font-bold text-amber-700">
                      {index + 1}
                    </span>
                    <p className="text-xs leading-relaxed text-slate-600">
                      {point}
                    </p>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                <span className="text-[11px] text-slate-400">掌握度</span>
                <span className="text-[11px] font-semibold text-slate-700">
                  待复习
                </span>
              </div>
              <ProgressBar value={42} tone="amber" className="mt-2" />
            </div>
          </div>

          <Link
            to="/chat"
            className="flex items-center justify-between gap-3 rounded-xl border border-slate-200 bg-white px-5 py-4 text-sm font-medium text-slate-700 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
          >
            <span className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-50">
                <BookOpenCheck className="h-4 w-4 text-violet-600" />
              </span>
              还有疑问？继续问 Agent
            </span>
            <ChevronRight className="h-4 w-4 text-slate-300" />
          </Link>
        </div>
      </div>
    </div>
  )
}
