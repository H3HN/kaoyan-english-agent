import { useMemo, useState } from 'react'
import {
  ArrowRight,
  BookMarked,
  CalendarDays,
  CheckCircle2,
  Eye,
  EyeOff,
  Layers,
  Play,
  Plus,
  RefreshCw,
  Trash2,
} from 'lucide-react'
import { EmptyState } from '../components/EmptyState'
import { PageHero } from '../components/PageHero'
import { ProgressBar } from '../components/ProgressBar'
import { StatCard } from '../components/StatCard'
import { Tag } from '../components/Tag'
import { useToast } from '../components/Toast'
import { formatDate } from '../lib/format'
import {
  REVIEW_INTERVALS,
  useAppStore,
} from '../store/AppStore'

type Tab = 'all' | 'review' | 'add'

function familiarityTone(value: number) {
  if (value >= 0.7) return 'emerald' as const
  if (value >= 0.4) return 'amber' as const
  return 'red' as const
}

export default function WordbookPage() {
  const { words, dueWords, addWord, removeWord, reviewWord, connected } =
    useAppStore()
  const [tab, setTab] = useState<Tab>('all')
  const [reviewedIds, setReviewedIds] = useState<string[]>([])
  const [sessionIds, setSessionIds] = useState<string[] | null>(null)
  const [revealed, setRevealed] = useState(false)
  const [form, setForm] = useState({ spelling: '', meaning: '', source: '' })
  const toast = useToast()

  const outlineCount = words.filter((word) => word.isOutline).length
  const averageFamiliarity =
    words.length > 0
      ? words.reduce((sum, word) => sum + word.familiarity, 0) / words.length
      : 0
  const reviewQueue = useMemo(() => {
    if (sessionIds) {
      const byId = new Map(words.map((word) => [word.id, word]))
      return sessionIds
        .filter((id) => !reviewedIds.includes(id))
        .map((id) => byId.get(id))
        .filter((word) => word !== undefined) as typeof words
    }
    return dueWords.filter((word) => !reviewedIds.includes(word.id))
  }, [sessionIds, words, dueWords, reviewedIds])
  const currentWord = reviewQueue[0]
  const reviewedCount = reviewedIds.length
  const totalDue = sessionIds ? sessionIds.length : reviewedCount + dueWords.length

  const startFreeReview = () => {
    if (words.length === 0) {
      toast('单词本还是空的，先添加单词再开始复习。', 'info')
      return
    }
    const ids = words.map((word) => word.id)
    for (let index = ids.length - 1; index > 0; index -= 1) {
      const target = Math.floor(Math.random() * (index + 1))
      ;[ids[index], ids[target]] = [ids[target], ids[index]]
    }
    setSessionIds(ids)
    setReviewedIds([])
    setRevealed(false)
    setTab('review')
    toast(`已随机生成 ${ids.length} 个单词的复习序列。`, 'success')
  }

  const handleAdd = () => {
    const result = addWord(form)
    if (!result.ok) {
      toast(result.message, 'error')
      return
    }
    toast(result.message, 'success')
    setForm({ spelling: '', meaning: '', source: '' })
  }

  const handleReview = (remembered: boolean) => {
    if (!currentWord) return
    reviewWord(currentWord.id, remembered)
    setReviewedIds((prev) => [...prev, currentWord.id])
    setRevealed(false)
    toast(
      remembered
        ? `“${currentWord.spelling}”已记住，复习间隔延长。`
        : `“${currentWord.spelling}”明天再复习一次。`,
      remembered ? 'success' : 'info',
    )
  }

  return (
    <div className="space-y-6">
      <PageHero
        eyebrow="VOCABULARY DESK"
        title="我的单词本"
        actions={
          <>
            <button
              type="button"
              onClick={startFreeReview}
              disabled={words.length === 0}
              className="inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 transition-colors hover:bg-slate-100 disabled:cursor-not-allowed disabled:bg-white/20 disabled:text-white/50"
            >
              <Play className="h-4 w-4" />
              开始复习
            </button>
            <button
              type="button"
              onClick={() => setTab('add')}
              className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-white/10"
            >
              <Plus className="h-4 w-4" />
              添加单词
            </button>
          </>
        }
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="总词数"
          value={words.length}
          icon={BookMarked}
          accent="blue"
        />
        <StatCard
          label="大纲词"
          value={outlineCount}
          icon={Layers}
          accent="cyan"
        />
        <StatCard
          label="待复习"
          value={dueWords.length}
          icon={CalendarDays}
          accent="amber"
        />
        <StatCard
          label="平均掌握度"
          value={`${Math.round(averageFamiliarity * 100)}%`}
          icon={RefreshCw}
          accent="violet"
        />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1 shadow-sm">
          {(
            [
              { id: 'all', label: '全部单词', count: words.length },
              { id: 'review', label: '今日复习', count: dueWords.length },
              { id: 'add', label: '添加单词', count: null },
            ] as const
          ).map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setTab(item.id)}
              className={`inline-flex items-center gap-1.5 rounded-md px-3.5 py-2 text-xs font-medium transition-colors ${
                tab === item.id
                  ? 'bg-slate-100 text-slate-900'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
              aria-pressed={tab === item.id}
            >
              {item.label}
              {item.count !== null ? (
                <span
                  className={`rounded-full px-1.5 py-0.5 text-[9px] ${
                    tab === item.id
                      ? 'bg-white text-slate-600'
                      : 'bg-slate-100 text-slate-400'
                  }`}
                >
                  {item.count}
                </span>
              ) : null}
            </button>
          ))}
        </div>
        <p className="flex items-center gap-1.5 text-[11px] text-slate-400">
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              connected ? 'bg-emerald-500' : 'bg-amber-500'
            }`}
          />
          {connected
            ? '已连接 FastAPI · 复习记录实时落库'
            : '本地模式 · 启动后端后自动同步'}
        </p>
      </div>

      {tab === 'all' ? (
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="hidden grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)_140px_110px_36px] border-b border-slate-100 bg-slate-50/70 px-5 py-3 text-[11px] font-medium text-slate-400 lg:grid">
            <span>单词 / 释义</span>
            <span>出处</span>
            <span>掌握度</span>
            <span>下次复习</span>
            <span />
          </div>

          {words.length > 0 ? (
            words.map((word) => {
              const percent = Math.round(word.familiarity * 100)
              const tone = familiarityTone(word.familiarity)
              const due = new Date(word.nextReview).getTime() <= Date.now()
              return (
                <div
                  key={word.id}
                  className="grid grid-cols-[minmax(0,1fr)_auto] gap-x-4 gap-y-3 border-b border-slate-100 px-5 py-4 last:border-b-0 lg:grid-cols-[minmax(0,1.5fr)_minmax(0,1fr)_140px_110px_36px] lg:items-center"
                >
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-serif text-[17px] font-semibold text-slate-900">
                        {word.spelling}
                      </span>
                      {word.phonetic ? (
                        <span className="text-[11px] text-slate-400">
                          {word.phonetic}
                        </span>
                      ) : null}
                      <Tag tone={word.isOutline ? 'emerald' : 'amber'}>
                        {word.isOutline ? '大纲词' : '非大纲'}
                      </Tag>
                    </div>
                    <p className="mt-1 text-xs text-slate-500">{word.meaning}</p>
                    <p className="mt-1 text-[10px] text-slate-400 lg:hidden">
                      {word.source}
                    </p>
                  </div>

                  <div className="hidden min-w-0 lg:block">
                    <Tag tone="slate">{word.source}</Tag>
                  </div>

                  <div className="col-span-2 lg:col-span-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] text-slate-400">掌握度</span>
                      <span className="text-[11px] font-semibold text-slate-700 tabular-nums">
                        {percent}%
                      </span>
                    </div>
                    <ProgressBar value={percent} tone={tone} className="mt-1.5" />
                  </div>

                  <div className="col-span-2 flex items-center justify-between lg:col-span-1 lg:block">
                    <span className="text-[10px] text-slate-400 lg:hidden">
                      下次复习
                    </span>
                    {due ? (
                      <Tag tone="amber" dot>
                        今天到期
                      </Tag>
                    ) : (
                      <span className="text-[11px] text-slate-500">
                        {formatDate(word.nextReview)}
                      </span>
                    )}
                  </div>

                  <div className="col-start-2 row-start-1 flex justify-end lg:col-start-5">
                    <button
                      type="button"
                      onClick={() => {
                        removeWord(word.id)
                        toast(`已从单词本移除“${word.spelling}”。`, 'info')
                      }}
                      aria-label={`删除 ${word.spelling}`}
                      title="从单词本移除"
                      className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-300 transition-colors hover:bg-red-50 hover:text-red-500"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              )
            })
          ) : (
            <div className="p-5">
              <EmptyState
                icon={BookMarked}
                title="单词本还是空的"
                action={
                  <button
                    type="button"
                    onClick={() => setTab('add')}
                    className="inline-flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2.5 text-xs font-semibold text-white hover:bg-slate-900"
                  >
                    <Plus className="h-3.5 w-3.5" />
                    添加第一个单词
                  </button>
                }
              />
            </div>
          )}
        </div>
      ) : null}

      {tab === 'review' ? (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
          <div>
            {currentWord ? (
              <>
                <div className="mb-3 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-slate-900">
                      {sessionIds ? '随机复习 · 全部单词' : '今日复习'}
                    </p>
                  </div>
                  <span className="text-[11px] font-medium text-slate-500 tabular-nums">
                    {reviewedCount + 1} / {totalDue || 1}
                  </span>
                </div>
                <ProgressBar
                  value={
                    totalDue > 0 ? (reviewedCount / totalDue) * 100 : 0
                  }
                  tone="amber"
                  className="mb-4"
                />

                <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
                  <div className="flex flex-wrap items-center gap-2">
                    <Tag tone={currentWord.isOutline ? 'emerald' : 'amber'}>
                      {currentWord.isOutline ? '大纲词' : '非大纲'}
                    </Tag>
                    <Tag tone="slate">{currentWord.source}</Tag>
                  </div>

                  <div className="mt-8 text-center">
                    <p className="font-serif text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
                      {currentWord.spelling}
                    </p>
                    {currentWord.phonetic ? (
                      <p className="mt-2 text-sm text-slate-400">
                        {currentWord.phonetic}
                      </p>
                    ) : null}
                    <p className="mt-2 text-[11px] text-slate-400">
                      已复习 {currentWord.reviewCount} 次 · 掌握度{' '}
                      {Math.round(currentWord.familiarity * 100)}%
                    </p>
                  </div>

                  <div className="mt-7">
                    {revealed ? (
                      <div className="rounded-xl border border-slate-200 bg-slate-50 px-5 py-4 text-center">
                        <p className="text-sm font-medium leading-7 text-slate-800">
                          {currentWord.meaning}
                        </p>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setRevealed(true)}
                        className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-slate-300 bg-slate-50/60 px-5 py-5 text-xs font-medium text-slate-500 transition-colors hover:border-slate-400 hover:bg-slate-50 hover:text-slate-700"
                      >
                        <Eye className="h-4 w-4" />
                        点击显示释义
                      </button>
                    )}
                  </div>

                  <div className="mt-6 grid gap-2 sm:grid-cols-2">
                    <button
                      type="button"
                      onClick={() => handleReview(false)}
                      disabled={!revealed}
                      className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 px-4 py-3 text-xs font-semibold text-slate-600 transition-colors hover:border-red-200 hover:bg-red-50 hover:text-red-700 disabled:opacity-40"
                    >
                      <EyeOff className="h-3.5 w-3.5" />
                      没记住 · 明天再来
                    </button>
                    <button
                      type="button"
                      onClick={() => handleReview(true)}
                      disabled={!revealed}
                      className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-800 px-4 py-3 text-xs font-semibold text-white transition-colors hover:bg-slate-900 disabled:bg-slate-200 disabled:text-slate-400"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      记住了 · 延长间隔
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <EmptyState
                icon={CheckCircle2}
                title={
                  sessionIds
                    ? '本轮随机复习完成'
                    : reviewedCount > 0
                      ? '今日复习完成'
                      : '今天没有待复习单词'
                }
                action={
                  <button
                    type="button"
                    onClick={() => {
                      setSessionIds(null)
                      setTab('all')
                    }}
                    className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-2.5 text-xs font-semibold text-slate-600 hover:bg-slate-50"
                  >
                    查看全部单词
                    <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                }
              />
            )}
          </div>

          <aside className="space-y-4">
            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center gap-2">
                <CalendarDays className="h-4 w-4 text-amber-500" />
                <h3 className="text-sm font-semibold text-slate-900">
                  艾宾浩斯节奏
                </h3>
              </div>
              <div className="mt-4 grid grid-cols-3 gap-1.5">
                {REVIEW_INTERVALS.map((day) => (
                  <span
                    key={day}
                    className="rounded-lg bg-slate-50 px-2 py-1.5 text-center text-[10px] font-medium text-slate-500 ring-1 ring-slate-100"
                  >
                    +{day} 天
                  </span>
                ))}
              </div>
              <div className="mt-4 border-t border-slate-100 pt-3">
                <p className="text-[10px] leading-relaxed text-slate-400">
                  当前队列。先复习拖得最久的词，避免间隔失真。
                </p>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="text-sm font-semibold text-slate-900">本次进度</h3>
              <div className="mt-4 space-y-3">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">已完成</span>
                  <span className="font-semibold text-slate-700">
                    {reviewedCount}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">剩余</span>
                  <span className="font-semibold text-slate-700">
                    {reviewQueue.length}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400">平均掌握度</span>
                  <span className="font-semibold text-slate-700">
                    {Math.round(averageFamiliarity * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </aside>
        </div>
      ) : null}

      {tab === 'add' ? (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_340px]">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
            <h2 className="text-sm font-semibold text-slate-900">手动添加</h2>

            <div className="mt-5 space-y-4">
              <div>
                <label
                  htmlFor="spelling"
                  className="text-[11px] font-medium text-slate-500"
                >
                  单词
                </label>
                <input
                  id="spelling"
                  value={form.spelling}
                  onChange={(event) =>
                    setForm((prev) => ({
                      ...prev,
                      spelling: event.target.value,
                    }))
                  }
                  placeholder="如：ubiquitous"
                  className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 outline-none transition-colors placeholder:text-slate-300 focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
                />
              </div>
              <div>
                <label
                  htmlFor="meaning"
                  className="text-[11px] font-medium text-slate-500"
                >
                  中文释义
                </label>
                <input
                  id="meaning"
                  value={form.meaning}
                  onChange={(event) =>
                    setForm((prev) => ({
                      ...prev,
                      meaning: event.target.value,
                    }))
                  }
                  placeholder="如：adj. 无处不在的；普遍存在的"
                  className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 outline-none transition-colors placeholder:text-slate-300 focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
                />
              </div>
              <div>
                <label
                  htmlFor="source"
                  className="text-[11px] font-medium text-slate-500"
                >
                  出处（可选）
                </label>
                <input
                  id="source"
                  value={form.source}
                  onChange={(event) =>
                    setForm((prev) => ({
                      ...prev,
                      source: event.target.value,
                    }))
                  }
                  placeholder="如：2024 英语一 Text 1"
                  className="mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3.5 py-2.5 text-sm text-slate-800 outline-none transition-colors placeholder:text-slate-300 focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10"
                />
              </div>
              <button
                type="button"
                onClick={handleAdd}
                className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-slate-800 px-4 py-3 text-xs font-semibold text-white transition-colors hover:bg-slate-900 sm:w-auto"
              >
                <Plus className="h-3.5 w-3.5" />
                加入单词本
              </button>
            </div>
          </div>

          <aside className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2">
              <CalendarDays className="h-4 w-4 text-blue-500" />
              <h3 className="text-sm font-semibold text-slate-900">
                加入后的复习计划
              </h3>
            </div>
            <div className="mt-4 space-y-2">
              {REVIEW_INTERVALS.map((day, index) => (
                <div
                  key={day}
                  className="flex items-center gap-3 rounded-lg border border-slate-100 bg-slate-50/60 px-3 py-2.5"
                >
                  <span className="flex h-5 w-5 items-center justify-center rounded-md bg-white text-[9px] font-bold text-slate-400 ring-1 ring-slate-200">
                    {index + 1}
                  </span>
                  <span className="flex-1 text-[11px] text-slate-500">
                    第 {index + 1} 次复习
                  </span>
                  <span className="text-[10px] font-medium text-slate-700">
                    +{day} 天
                  </span>
                </div>
              ))}
            </div>
          </aside>
        </div>
      ) : null}
    </div>
  )
}
