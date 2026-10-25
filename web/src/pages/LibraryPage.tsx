import { useEffect, useMemo, useState } from 'react'
import {
  ArrowRight,
  Check,
  ChevronLeft,
  ChevronRight,
  Layers,
  Loader2,
  Plus,
  Search,
  Target,
} from 'lucide-react'
import { Link, useSearchParams } from 'react-router-dom'
import { PageHero } from '../components/PageHero'
import { Tag } from '../components/Tag'
import { useToast } from '../components/Toast'
import {
  api,
  type PassageSummary,
  type VocabListResponse,
} from '../lib/api'
import { useAppStore } from '../store/AppStore'

type Tab = 'vocab' | 'exams'

const PAGE_SIZE = 50

const LEVELS = ['全部', '基础', '核心', '拔高'] as const

const levelTone: Record<string, 'slate' | 'emerald' | 'blue' | 'amber'> = {
  基础: 'slate',
  核心: 'emerald',
  拔高: 'amber',
}

export default function LibraryPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const tab: Tab = searchParams.get('tab') === 'exams' ? 'exams' : 'vocab'
  const setTab = (next: Tab) => {
    const params = new URLSearchParams(searchParams)
    params.set('tab', next)
    setSearchParams(params, { replace: true })
  }

  return (
    <div className="space-y-6">
      <PageHero
        eyebrow="MATERIAL LIBRARY"
        title="资料库"
        subtitle="直接翻阅考研大纲词库与已发布的真题篇章，看到有用的内容一键收进「我的单词本」，或跳去对应训练页。"
        actions={
          <div className="flex items-center gap-2 rounded-xl border border-white/15 bg-white/5 p-1">
            <button
              type="button"
              onClick={() => setTab('vocab')}
              className={`inline-flex items-center gap-1.5 rounded-lg px-3.5 py-2 text-xs font-semibold transition-colors ${
                tab === 'vocab'
                  ? 'bg-white text-slate-900'
                  : 'text-slate-300 hover:bg-white/10 hover:text-white'
              }`}
            >
              <Layers className="h-3.5 w-3.5" strokeWidth={2} />
              大纲词汇
            </button>
            <button
              type="button"
              onClick={() => setTab('exams')}
              className={`inline-flex items-center gap-1.5 rounded-lg px-3.5 py-2 text-xs font-semibold transition-colors ${
                tab === 'exams'
                  ? 'bg-white text-slate-900'
                  : 'text-slate-300 hover:bg-white/10 hover:text-white'
              }`}
            >
              <Target className="h-3.5 w-3.5" strokeWidth={2} />
              真题篇章
            </button>
          </div>
        }
      />

      {tab === 'vocab' ? <VocabBrowser /> : <ExamBrowser />}
    </div>
  )
}

function VocabBrowser() {
  const { words, addWord } = useAppStore()
  const toast = useToast()
  const [input, setInput] = useState('')
  const [query, setQuery] = useState('')
  const [level, setLevel] = useState<string>('全部')
  const [sort, setSort] = useState<'freq' | 'alpha'>('freq')
  const [page, setPage] = useState(0)
  const [jump, setJump] = useState('')
  const [data, setData] = useState<VocabListResponse>({ items: [], total: 0 })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setQuery(input.trim())
      setPage(0)
    }, 300)
    return () => window.clearTimeout(timer)
  }, [input])

  useEffect(() => {
    let alive = true
    setLoading(true)
    setError(false)
    api
      .browseVocab({
        q: query,
        level: level === '全部' ? '' : level,
        sort,
        offset: page * PAGE_SIZE,
        limit: PAGE_SIZE,
      })
      .then((response) => {
        if (alive) setData(response)
      })
      .catch(() => {
        if (alive) setError(true)
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => {
      alive = false
    }
  }, [query, level, sort, page])

  const saved = useMemo(
    () => new Set(words.map((word) => word.spelling.toLowerCase())),
    [words],
  )
  const pageCount = Math.max(1, Math.ceil(data.total / PAGE_SIZE))

  const visiblePages = useMemo(() => {
    const size = 5
    let start = Math.max(0, page - Math.floor(size / 2))
    const end = Math.min(pageCount - 1, start + size - 1)
    start = Math.max(0, end - size + 1)
    return Array.from({ length: end - start + 1 }, (_, index) => start + index)
  }, [page, pageCount])

  const goToPage = (target: number) => {
    setPage(Math.min(pageCount - 1, Math.max(0, target)))
  }

  const handleJump = () => {
    const target = Number(jump)
    if (!Number.isFinite(target) || target < 1) return
    goToPage(Math.round(target) - 1)
    setJump('')
  }

  const handleAdd = (word: string, meaning: string) => {
    const result = addWord({
      spelling: word,
      meaning,
      source: '大纲词库',
    })
    toast(result.message, result.ok ? 'success' : 'info')
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="搜索单词或释义，例如 abandon / 放弃"
            className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2.5 pl-9 pr-3 text-sm text-slate-800 outline-none transition-colors placeholder:text-slate-400 focus:border-slate-400 focus:bg-white"
          />
        </div>
        <div className="flex items-center gap-2">
          <select
            value={level}
            onChange={(event) => {
              setLevel(event.target.value)
              setPage(0)
            }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-xs font-medium text-slate-600 outline-none focus:border-slate-400"
          >
            {LEVELS.map((item) => (
              <option key={item} value={item}>
                {item === '全部' ? '全部等级' : item}
              </option>
            ))}
          </select>
          <select
            value={sort}
            onChange={(event) => {
              setSort(event.target.value as 'freq' | 'alpha')
              setPage(0)
            }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-xs font-medium text-slate-600 outline-none focus:border-slate-400"
          >
            <option value="freq">按真题频次</option>
            <option value="alpha">按字母顺序</option>
          </select>
        </div>
      </div>

      <div className="flex items-center justify-between px-1">
        <p className="text-xs text-slate-500">
          共 <span className="font-semibold text-slate-700">{data.total.toLocaleString('zh-CN')}</span> 条
          {query ? ` · 匹配「${query}」` : ''}
        </p>
        <p className="text-[11px] text-slate-400">
          频次 = 当前题库内出现次数，题库扩充后会自动更新
        </p>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
        {loading ? (
          <div className="flex items-center justify-center gap-2 py-16 text-sm text-slate-400">
            <Loader2 className="h-4 w-4 animate-spin" />
            正在读取词库…
          </div>
        ) : error ? (
          <p className="py-16 text-center text-sm text-red-500">
            词库读取失败，请确认后端已启动。
          </p>
        ) : data.items.length === 0 ? (
          <p className="py-16 text-center text-sm text-slate-400">
            没有匹配的词汇，换个关键词试试。
          </p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {data.items.map((row) => {
              const added = saved.has(row.word.toLowerCase())
              return (
                <li
                  key={row.word}
                  className="flex flex-col gap-3 px-4 py-3 transition-colors hover:bg-slate-50/70 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-semibold text-slate-900">
                        {row.word}
                      </span>
                      <Tag tone={levelTone[row.level] ?? 'slate'}>{row.level}</Tag>
                      <span className="text-[11px] text-slate-400">
                        题库出现 {row.exam_frequency} 次
                      </span>
                    </div>
                    <p className="mt-1 text-xs leading-relaxed text-slate-600">
                      {row.basic_meaning}
                    </p>
                    {row.rare_meaning ? (
                      <p className="mt-0.5 text-[11px] leading-relaxed text-amber-700">
                        僻义：{row.rare_meaning}
                      </p>
                    ) : null}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleAdd(row.word, row.basic_meaning)}
                    disabled={added}
                    className={`inline-flex shrink-0 items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
                      added
                        ? 'cursor-default bg-emerald-50 text-emerald-700'
                        : 'bg-slate-900 text-white hover:bg-slate-700'
                    }`}
                  >
                    {added ? (
                      <>
                        <Check className="h-3.5 w-3.5" />
                        已在单词本
                      </>
                    ) : (
                      <>
                        <Plus className="h-3.5 w-3.5" />
                        加入单词本
                      </>
                    )}
                  </button>
                </li>
              )
            })}
          </ul>
        )}
      </div>

      {data.total > PAGE_SIZE ? (
        <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white px-3 py-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-1.5">
            <button
              type="button"
              onClick={() => goToPage(page - 1)}
              disabled={page === 0}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-2 text-xs font-medium text-slate-600 transition-colors hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              上一页
            </button>
            {visiblePages.map((index) => (
              <button
                key={index}
                type="button"
                onClick={() => goToPage(index)}
                aria-current={index === page ? 'page' : undefined}
                className={`min-w-[32px] rounded-lg px-2 py-2 text-xs font-semibold tabular-nums transition-colors ${
                  index === page
                    ? 'bg-slate-900 text-white'
                    : 'border border-slate-200 text-slate-600 hover:border-slate-300'
                }`}
              >
                {index + 1}
              </button>
            ))}
            <button
              type="button"
              onClick={() => goToPage(page + 1)}
              disabled={page >= pageCount - 1}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-2 text-xs font-medium text-slate-600 transition-colors hover:border-slate-300 disabled:cursor-not-allowed disabled:opacity-40"
            >
              下一页
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">
              第 {page + 1} / {pageCount} 页
            </span>
            <span className="text-slate-300">|</span>
            <label className="flex items-center gap-1.5 text-xs text-slate-500">
              跳到
              <input
                value={jump}
                onChange={(event) =>
                  setJump(event.target.value.replace(/[^0-9]/g, ''))
                }
                onKeyDown={(event) => {
                  if (event.key === 'Enter') handleJump()
                }}
                inputMode="numeric"
                placeholder={String(page + 1)}
                className="w-14 rounded-lg border border-slate-200 px-2 py-1.5 text-center text-xs text-slate-800 outline-none transition-colors placeholder:text-slate-300 focus:border-slate-400"
              />
              页
            </label>
            <button
              type="button"
              onClick={handleJump}
              disabled={!jump}
              className="rounded-lg bg-slate-900 px-2.5 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              跳转
            </button>
          </div>
        </div>
      ) : null}
    </section>
  )
}

function ExamBrowser() {
  const [passages, setPassages] = useState<PassageSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    let alive = true
    api
      .getPassages()
      .then((response) => {
        if (!alive) return
        setPassages(
          [...response.items].sort(
            (a, b) =>
              b.year - a.year || a.text_number - b.text_number,
          ),
        )
      })
      .catch(() => {
        if (alive) setError(true)
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => {
      alive = false
    }
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white py-16 text-sm text-slate-400">
        <Loader2 className="h-4 w-4 animate-spin" />
        正在读取真题库…
      </div>
    )
  }

  if (error) {
    return (
      <p className="rounded-xl border border-slate-200 bg-white py-16 text-center text-sm text-red-500">
        真题库读取失败，请确认后端已启动。
      </p>
    )
  }

  if (passages.length === 0) {
    return (
      <p className="rounded-xl border border-slate-200 bg-white py-16 text-center text-sm text-slate-400">
        暂无已发布的真题篇章，发布后即可开始学习。
      </p>
    )
  }

  return (
    <section className="grid gap-4 md:grid-cols-2">
      {passages.map((passage) => {
        const href = `/options?year=${passage.year}&exam=${encodeURIComponent(
          passage.exam_type,
        )}&text=${passage.text_number}`
        return (
          <article
            key={passage.id}
            className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/[0.02]"
          >
            <div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-slate-900">
                  {passage.year} {passage.exam_type} Text {passage.text_number}
                </span>
                <Tag tone="emerald">学习篇章</Tag>
              </div>
              <p className="mt-2 line-clamp-3 text-xs leading-relaxed text-slate-500">
                {passage.preview}
              </p>
              <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-slate-400">
                <span>{passage.char_count} 词</span>
                <span>{passage.sentence_count} 句</span>
                <span>{passage.question_count} 题</span>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-2">
              {passage.question_count > 0 ? (
                <Link
                  to={href}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-slate-700"
                >
                  去做题
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              ) : (
                <span className="rounded-lg bg-slate-100 px-3 py-2 text-xs font-medium text-slate-400">
                  暂无题目
                </span>
              )}
              <Link
                to="/sentence"
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600 transition-colors hover:border-slate-300 hover:text-slate-900"
              >
                拆解句子
                <ArrowRight className="h-3.5 w-3.5" />
              </Link>
            </div>
          </article>
        )
      })}
    </section>
  )
}
