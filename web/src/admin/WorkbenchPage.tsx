import { useCallback, useEffect, useRef, useState } from 'react'
import {
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  FileJson,
  History,
  Loader2,
  RefreshCw,
  Search,
  Send,
  ShieldCheck,
  Undo2,
  UploadCloud,
  X,
} from 'lucide-react'
import {
  AdminAuthError,
  adminApi,
  type AdminEvent,
  type AdminImportResult,
  type AdminPage,
  type AdminPassage,
  type AdminStats,
} from '../lib/adminApi'
import { formatRelative } from '../lib/format'
import { useAdminAuth } from './AdminLayout'

interface ActionSpec {
  action: string
  label: string
  enabledFor: AdminPassage['publication_status'][]
  tone: 'primary' | 'ghost' | 'danger'
  confirm: boolean
  description: string
}

const ACTIONS: ActionSpec[] = [
  {
    action: 'review',
    label: '审核通过',
    enabledFor: ['draft'],
    tone: 'primary',
    confirm: false,
    description: '审核通过后篇章进入待发布状态，题目标记为已审核。',
  },
  {
    action: 'publish',
    label: '发布',
    enabledFor: ['reviewed'],
    tone: 'primary',
    confirm: true,
    description: '发布后学生端立即可见，请确认解析与证据已核对。',
  },
  {
    action: 'publish-practice',
    label: '仅开练习',
    enabledFor: ['draft'],
    tone: 'ghost',
    confirm: true,
    description:
      '不宣称解析已审核，仅开放基础练习；要求答案来源与切句完整。',
  },
  {
    action: 'withdraw',
    label: '撤回',
    enabledFor: ['reviewed', 'published'],
    tone: 'danger',
    confirm: true,
    description:
      '撤回不会删除原始 PDF 与切片，篇章回到草稿，学生端不可见。',
  },
]

const STATUS_TABS = [
  { value: '', label: '全部' },
  { value: 'draft', label: '草稿' },
  { value: 'reviewed', label: '待发布' },
  { value: 'published', label: '已发布' },
] as const

const STATUS_TONE: Record<AdminPassage['publication_status'], string> = {
  draft: 'bg-[#EDE7DC] text-[#6B6559]',
  reviewed: 'bg-[#FBF0DA] text-[#9A6B1F]',
  published: 'bg-[#EAF2EE] text-[#2F6F5E]',
}

const EMPTY_STATS: AdminStats = {
  draft: 0,
  reviewed: 0,
  published: 0,
  total: 0,
  question_total: 0,
  sentence_total: 0,
}

export default function WorkbenchPage() {
  const { lock } = useAdminAuth()
  const [stats, setStats] = useState<AdminStats>(EMPTY_STATS)
  const [page, setPage] = useState<AdminPage | null>(null)
  const [statusFilter, setStatusFilter] = useState('')
  const [keyword, setKeyword] = useState('')
  const [appliedKeyword, setAppliedKeyword] = useState('')
  const [pageIndex, setPageIndex] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [importText, setImportText] = useState('')
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<AdminImportResult | null>(null)
  const [confirm, setConfirm] = useState<{
    passage: AdminPassage
    spec: ActionSpec
  } | null>(null)
  const [actingId, setActingId] = useState('')
  const [eventsFor, setEventsFor] = useState<{
    id: string
    items: AdminEvent[]
    loading: boolean
  } | null>(null)
  const fileInput = useRef<HTMLInputElement | null>(null)

  const handleFailure = useCallback(
    (caught: unknown) => {
      if (caught instanceof AdminAuthError) {
        lock()
        return
      }
      setError(caught instanceof Error ? caught.message : '请求失败')
    },
    [lock],
  )

  const load = useCallback(() => {
    setLoading(true)
    Promise.all([
      adminApi.getStats(),
      adminApi.listPassages({
        status: statusFilter,
        q: appliedKeyword,
        page: pageIndex,
        pageSize: 10,
      }),
    ])
      .then(([statsData, pageData]) => {
        setStats(statsData)
        setPage(pageData)
        setError('')
      })
      .catch(handleFailure)
      .finally(() => setLoading(false))
  }, [statusFilter, appliedKeyword, pageIndex, handleFailure])

  useEffect(() => {
    load()
  }, [load])

  const runAction = async (passage: AdminPassage, spec: ActionSpec) => {
    setActingId(passage.id)
    setError('')
    try {
      await adminApi.transition(passage.id, spec.action)
      setConfirm(null)
      load()
    } catch (caught) {
      handleFailure(caught)
    } finally {
      setActingId('')
    }
  }

  const requestAction = (passage: AdminPassage, spec: ActionSpec) => {
    if (spec.confirm) {
      setConfirm({ passage, spec })
      return
    }
    void runAction(passage, spec)
  }

  const runImport = async () => {
    const text = importText.trim()
    if (!text) {
      setError('请先粘贴题库 JSON 或选择文件')
      return
    }
    let document: unknown
    try {
      document = JSON.parse(text)
    } catch {
      setError('JSON 解析失败，请检查粘贴内容')
      return
    }
    setImporting(true)
    setError('')
    setImportResult(null)
    try {
      const result = await adminApi.importDocument(document)
      setImportResult(result)
      if (result.ok) setImportText('')
      load()
    } catch (caught) {
      handleFailure(caught)
    } finally {
      setImporting(false)
    }
  }

  const toggleEvents = async (passage: AdminPassage) => {
    if (eventsFor?.id === passage.id) {
      setEventsFor(null)
      return
    }
    setEventsFor({ id: passage.id, items: [], loading: true })
    try {
      const data = await adminApi.getEvents(passage.id)
      setEventsFor({ id: passage.id, items: data.items, loading: false })
    } catch (caught) {
      setEventsFor(null)
      handleFailure(caught)
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-lg font-bold text-[#26312C]">题库导入工作台</h1>
          <p className="mt-1 text-[11px] text-[#8C867B]">
            维护考纲题库：导入草稿、人工审核、发布或撤回，全部写入本地演示库并记录审计。
          </p>
        </div>
        <button
          type="button"
          onClick={load}
          className="inline-flex shrink-0 items-center gap-1.5 self-start rounded-lg border border-[#D8D2C6] bg-white px-3 py-2 text-[11px] font-medium text-[#3E4A43] transition-colors hover:bg-[#F7F4EE] sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          重新加载
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[
          { label: '草稿', value: stats.draft, hint: '待审核', icon: FileJson },
          { label: '待发布', value: stats.reviewed, hint: '已审核', icon: ShieldCheck },
          { label: '已发布', value: stats.published, hint: '学生端可见', icon: CheckCircle2 },
          {
            label: '题目 / 句子',
            value: `${stats.question_total} / ${stats.sentence_total}`,
            hint: '全部篇章',
            icon: ClipboardList,
          },
        ].map(({ label, value, hint, icon: Icon }) => (
          <div
            key={label}
            className="rounded-xl border border-[#E5DFD3] bg-white px-4 py-3.5 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-medium text-[#9A948A]">{label}</span>
              <Icon className="h-3.5 w-3.5 text-[#B8B1A4]" />
            </div>
            <p className="mt-1.5 text-xl font-bold tabular-nums text-[#26312C]">
              {value}
            </p>
            <p className="mt-0.5 text-[10px] text-[#B8B1A4]">{hint}</p>
          </div>
        ))}
      </div>

      {error ? (
        <div className="flex items-start gap-2 rounded-lg border border-[#F0D3CC] bg-[#FBEDEA] px-3.5 py-2.5 text-[11px] text-[#C05746]">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span className="flex-1">{error}</span>
          <button
            type="button"
            aria-label="关闭错误提示"
            onClick={() => setError('')}
            className="shrink-0 text-[#C05746]/60 hover:text-[#C05746]"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      ) : null}

      <section className="rounded-xl border border-[#E5DFD3] bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-[#EDE7DC] px-5 py-3.5">
          <div className="flex items-center gap-2">
            <UploadCloud className="h-4 w-4 text-[#2F6F5E]" strokeWidth={1.8} />
            <span className="text-xs font-semibold text-[#26312C]">导入题库草稿</span>
          </div>
          <input
            ref={fileInput}
            type="file"
            accept=".json,application/json"
            className="hidden"
            onChange={async (event) => {
              const file = event.target.files?.[0]
              if (!file) return
              setImportText(await file.text())
              setImportResult(null)
              event.target.value = ''
            }}
          />
          <button
            type="button"
            onClick={() => fileInput.current?.click()}
            className="rounded-lg border border-[#D8D2C6] px-2.5 py-1.5 text-[10px] font-medium text-[#6B6559] transition-colors hover:bg-[#F7F4EE] hover:text-[#26312C]"
          >
            选择 JSON 文件
          </button>
        </div>
        <div className="p-5">
          <textarea
            value={importText}
            onChange={(event) => setImportText(event.target.value)}
            spellCheck={false}
            placeholder='{"format":"kaoyan-question-bank-v1","passages":[...]}'
            className="h-32 w-full resize-y rounded-lg border border-[#E5DFD3] bg-[#FCFBF8] px-3 py-2.5 font-mono text-[11px] leading-relaxed text-[#3E4A43] outline-none focus:border-[#2F6F5E]"
          />
          <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
            <p className="text-[10px] text-[#9A948A]">
              导入后默认为草稿；每篇须满足原卷 5 题、答案来源与来源说明。
            </p>
            <button
              type="button"
              onClick={() => void runImport()}
              disabled={importing}
              className="inline-flex items-center gap-1.5 rounded-lg bg-[#2F6F5E] px-3.5 py-2 text-[11px] font-semibold text-white transition-colors hover:bg-[#275c4e] disabled:opacity-60"
            >
              {importing ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Send className="h-3.5 w-3.5" />
              )}
              {importing ? '正在导入…' : '导入到草稿'}
            </button>
          </div>
          {importResult ? (
            <div
              className={`mt-3 rounded-lg border px-3.5 py-2.5 text-[11px] ${
                importResult.ok
                  ? 'border-[#CFE5DA] bg-[#EAF2EE] text-[#2F6F5E]'
                  : 'border-[#F0D3CC] bg-[#FBEDEA] text-[#C05746]'
              }`}
            >
              <p className="font-semibold">
                导入完成：成功 {importResult.succeeded} 篇，失败 {importResult.failed} 篇
              </p>
              {importResult.results
                .filter((item) => !item.ok)
                .map((item) => (
                  <p key={item.index} className="mt-1">
                    第 {item.index} 项：{item.error}
                  </p>
                ))}
            </div>
          ) : null}
        </div>
      </section>

      <section className="rounded-xl border border-[#E5DFD3] bg-white shadow-sm">
        <div className="flex flex-col gap-3 border-b border-[#EDE7DC] px-5 py-3.5 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-1.5">
            {STATUS_TABS.map((tab) => (
              <button
                key={tab.value || 'all'}
                type="button"
                onClick={() => {
                  setStatusFilter(tab.value)
                  setPageIndex(1)
                }}
                className={`rounded-lg px-2.5 py-1.5 text-[11px] font-medium transition-colors ${
                  statusFilter === tab.value
                    ? 'bg-[#1F4E43] text-white'
                    : 'text-[#6B6559] hover:bg-[#F7F4EE] hover:text-[#26312C]'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <form
            className="flex items-center gap-2"
            onSubmit={(event) => {
              event.preventDefault()
              setAppliedKeyword(keyword.trim())
              setPageIndex(1)
            }}
          >
            <div className="flex items-center gap-1.5 rounded-lg border border-[#E5DFD3] bg-white px-2.5">
              <Search className="h-3.5 w-3.5 text-[#B8B1A4]" />
              <input
                value={keyword}
                onChange={(event) => setKeyword(event.target.value)}
                placeholder="年份 / 试卷 / 篇章 ID"
                className="w-40 bg-transparent py-1.5 text-[11px] text-[#3E4A43] outline-none"
              />
            </div>
            <button
              type="submit"
              className="rounded-lg bg-[#F7F4EE] px-2.5 py-1.5 text-[10px] font-medium text-[#6B6559] transition-colors hover:bg-[#EDE7DC] hover:text-[#26312C]"
            >
              搜索
            </button>
          </form>
        </div>

        <div className="hidden grid-cols-[1.3fr_0.8fr_0.7fr_1fr_1.6fr] gap-3 border-b border-[#EDE7DC] bg-[#FCFBF8] px-5 py-2.5 text-[10px] font-medium text-[#9A948A] sm:grid">
          <span>年度 / Text</span>
          <span>题数 / 句数</span>
          <span>状态</span>
          <span>最近操作</span>
          <span className="text-right">操作</span>
        </div>

        {page?.items.length ? (
          page.items.map((passage) => (
            <div key={passage.id} className="border-b border-[#EDE7DC] last:border-b-0">
              <div className="flex flex-col gap-2.5 px-5 py-3.5 sm:grid sm:grid-cols-[1.3fr_0.8fr_0.7fr_1fr_1.6fr] sm:items-center sm:gap-3">
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-[#26312C]">
                    {passage.year} {passage.exam_type} · Text {passage.text_number}
                  </p>
                  <p className="mt-0.5 truncate font-mono text-[10px] text-[#B8B1A4]">
                    {passage.id}
                  </p>
                </div>
                <span className="text-[11px] text-[#6B6559] tabular-nums">
                  {passage.question_count} / {passage.sentence_count}
                </span>
                <span>
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium ${STATUS_TONE[passage.publication_status]}`}
                  >
                    {passage.status_label}
                  </span>
                </span>
                <div className="flex items-center gap-2 text-[10px] text-[#9A948A]">
                  <span>{formatRelative(passage.last_event_at ?? '')}</span>
                  <button
                    type="button"
                    onClick={() => void toggleEvents(passage)}
                    className="inline-flex items-center gap-0.5 text-[#6B6559] hover:text-[#26312C]"
                  >
                    <History className="h-3 w-3" />
                    记录
                  </button>
                </div>
                <div className="flex flex-wrap items-center justify-start gap-1.5 sm:justify-end">
                  {ACTIONS.filter((spec) =>
                    spec.enabledFor.includes(passage.publication_status),
                  ).map((spec) => (
                    <button
                      key={spec.action}
                      type="button"
                      disabled={actingId === passage.id}
                      onClick={() => requestAction(passage, spec)}
                      className={`inline-flex items-center gap-1 rounded-md px-2 py-1.5 text-[10px] font-medium transition-colors disabled:opacity-50 ${
                        spec.tone === 'primary'
                          ? 'bg-[#2F6F5E] text-white hover:bg-[#275c4e]'
                          : spec.tone === 'danger'
                            ? 'bg-[#C05746] text-white hover:bg-[#a94a3b]'
                            : 'border border-[#D8D2C6] text-[#3E4A43] hover:bg-[#F7F4EE]'
                      }`}
                    >
                      {spec.tone === 'danger' ? (
                        <Undo2 className="h-3 w-3" />
                      ) : null}
                      {actingId === passage.id ? '处理中…' : spec.label}
                    </button>
                  ))}
                </div>
              </div>
              {eventsFor?.id === passage.id ? (
                <div className="bg-[#FCFBF8] px-5 py-2.5">
                  {eventsFor.loading ? (
                    <p className="text-[10px] text-[#9A948A]">正在读取审计记录…</p>
                  ) : (
                    <ul className="space-y-1">
                      {eventsFor.items.map((event) => (
                        <li
                          key={event.id}
                          className="flex items-center gap-2 text-[10px] text-[#6B6559]"
                        >
                          <span className="w-16 shrink-0 font-mono text-[#B8B1A4]">
                            {event.created_at.slice(5, 16).replace('T', ' ')}
                          </span>
                          <span className="rounded bg-[#EDE7DC] px-1.5 py-0.5 font-medium">
                            {event.action}
                          </span>
                          <span className="text-[#9A948A]">
                            rev {event.revision} · {event.actor}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ) : null}
            </div>
          ))
        ) : (
          <div className="px-5 py-12 text-center">
            <p className="text-xs font-medium text-[#6B6559]">
              {loading ? '正在读取题库…' : '本地演示库暂无匹配记录'}
            </p>
            <p className="mt-1 text-[10px] text-[#B8B1A4]">
              可在上方导入题库 JSON 创建草稿。
            </p>
          </div>
        )}

        <div className="flex items-center justify-between border-t border-[#EDE7DC] px-5 py-2.5">
          <span className="text-[10px] text-[#9A948A]">
            共 {page?.total ?? 0} 篇 · 第 {page?.page ?? 1} / {page?.pages ?? 1} 页
          </span>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              disabled={!page || page.page <= 1}
              onClick={() => setPageIndex((index) => Math.max(1, index - 1))}
              className="flex h-6 w-6 items-center justify-center rounded border border-[#E5DFD3] text-[#6B6559] transition-colors hover:bg-[#F7F4EE] disabled:opacity-40"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
            </button>
            <button
              type="button"
              disabled={!page || page.page >= page.pages}
              onClick={() =>
                setPageIndex((index) =>
                  page ? Math.min(page.pages, index + 1) : index,
                )
              }
              className="flex h-6 w-6 items-center justify-center rounded border border-[#E5DFD3] text-[#6B6559] transition-colors hover:bg-[#F7F4EE] disabled:opacity-40"
            >
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </section>

      <p className="text-[10px] text-[#9A948A]">
        数据来源：exam_passages / exam_sentences / exam_questions / bank_events
      </p>

      {confirm ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#26312C]/40 px-4">
          <div className="w-full max-w-sm rounded-xl border border-[#E5DFD3] bg-white p-5 shadow-xl">
            <p className="text-sm font-bold text-[#26312C]">
              {confirm.spec.label} · {confirm.passage.year}{' '}
              {confirm.passage.exam_type} Text {confirm.passage.text_number}
            </p>
            <p className="mt-2 text-[11px] leading-relaxed text-[#6B6559]">
              {confirm.spec.description}
            </p>
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setConfirm(null)}
                className="rounded-lg border border-[#D8D2C6] px-3 py-1.5 text-[11px] font-medium text-[#6B6559] transition-colors hover:bg-[#F7F4EE]"
              >
                取消
              </button>
              <button
                type="button"
                disabled={actingId === confirm.passage.id}
                onClick={() => void runAction(confirm.passage, confirm.spec)}
                className={`rounded-lg px-3 py-1.5 text-[11px] font-semibold text-white transition-colors disabled:opacity-60 ${
                  confirm.spec.tone === 'danger'
                    ? 'bg-[#C05746] hover:bg-[#a94a3b]'
                    : 'bg-[#2F6F5E] hover:bg-[#275c4e]'
                }`}
              >
                {actingId === confirm.passage.id ? '处理中…' : `确认${confirm.spec.label}`}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}