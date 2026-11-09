import { useCallback, useEffect, useState } from 'react'
import {
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  FileJson,
  History,
  LibraryBig,
  Loader2,
  Pencil,
  Plus,
  Power,
  Save,
  Search,
  ShieldAlert,
  X,
} from 'lucide-react'
import {
  AdminAuthError,
  adminApi,
  type TrapPayload,
  type TrapRule,
  type VocabCitation,
  type VocabEntry,
  type VocabPage,
  type VocabPayload,
} from '../lib/adminApi'
import { useAdminAuth } from './AdminLayout'

const LEVELS = ['', '核心', '高频', '中频', '基础']
const LEVEL_TONE: Record<string, string> = {
  核心: 'bg-[#EAF2EE] text-[#2F6F5E]',
  高频: 'bg-[#EEF4F1] text-[#3E7F6C]',
  中频: 'bg-[#F6F1E6] text-[#8A6A2F]',
  基础: 'bg-[#EDE7DC] text-[#6B6559]',
}

const emptyVocab: VocabPayload = {
  word: '',
  phonetic: '',
  basic_meaning: '',
  rare_meaning: '',
  exam_frequency: 0,
  level: '基础',
  enabled: true,
}

interface DrawerState {
  mode: 'edit' | 'create'
  draft: VocabPayload
  citations: VocabCitation[]
  loading: boolean
}

export default function KnowledgePage() {
  const { lock } = useAdminAuth()
  const [tab, setTab] = useState<'vocab' | 'traps' | 'prompt'>('vocab')
  const [vocabPage, setVocabPage] = useState<VocabPage | null>(null)
  const [keyword, setKeyword] = useState('')
  const [appliedKeyword, setAppliedKeyword] = useState('')
  const [level, setLevel] = useState('')
  const [enabledFilter, setEnabledFilter] = useState('')
  const [pageIndex, setPageIndex] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [drawer, setDrawer] = useState<DrawerState | null>(null)
  const [saving, setSaving] = useState(false)
  const [traps, setTraps] = useState<TrapRule[] | null>(null)
  const [trapEditor, setTrapEditor] = useState<{
    id: number | null
    draft: TrapPayload
  } | null>(null)
  const [trapSaving, setTrapSaving] = useState(false)

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

  const loadVocab = useCallback(() => {
    setLoading(true)
    adminApi
      .listVocab({
        keyword: appliedKeyword,
        level,
        enabled: enabledFilter,
        page: pageIndex,
        pageSize: 20,
      })
      .then((data) => {
        setVocabPage(data)
        setError('')
      })
      .catch(handleFailure)
      .finally(() => setLoading(false))
  }, [appliedKeyword, level, enabledFilter, pageIndex, handleFailure])

  useEffect(() => {
    loadVocab()
  }, [loadVocab])

  useEffect(() => {
    if (tab !== 'traps' || traps) return
    adminApi
      .listTrapRules()
      .then((data) => setTraps(data.items))
      .catch(handleFailure)
  }, [tab, traps, handleFailure])

  const openEdit = (entry: VocabEntry) => {
    setDrawer({
      mode: 'edit',
      draft: { ...entry },
      citations: [],
      loading: true,
    })
    adminApi
      .getVocab(entry.word)
      .then((detail) =>
        setDrawer((current) =>
          current
            ? {
                ...current,
                draft: {
                  word: detail.word,
                  phonetic: detail.phonetic,
                  basic_meaning: detail.basic_meaning,
                  rare_meaning: detail.rare_meaning,
                  exam_frequency: detail.exam_frequency,
                  level: detail.level,
                  enabled: detail.enabled,
                },
                citations: detail.citations,
                loading: false,
              }
            : current,
        ),
      )
      .catch((caught) => {
        handleFailure(caught)
        setDrawer((current) => (current ? { ...current, loading: false } : current))
      })
  }

  const openCreate = () => {
    setDrawer({
      mode: 'create',
      draft: { ...emptyVocab },
      citations: [],
      loading: false,
    })
  }

  const saveDrawer = async () => {
    if (!drawer) return
    if (!drawer.draft.word.trim() || !drawer.draft.basic_meaning.trim()) {
      setError('单词与基本释义不能为空')
      return
    }
    setSaving(true)
    setError('')
    try {
      if (drawer.mode === 'create') {
        await adminApi.createVocab(drawer.draft)
      } else {
        await adminApi.updateVocab(drawer.draft.word, drawer.draft)
      }
      setDrawer(null)
      loadVocab()
    } catch (caught) {
      handleFailure(caught)
    } finally {
      setSaving(false)
    }
  }

  const toggleEntry = async (entry: VocabEntry) => {
    try {
      await adminApi.toggleVocab(entry.word, !entry.enabled)
      loadVocab()
    } catch (caught) {
      handleFailure(caught)
    }
  }

  const saveTrap = async () => {
    if (!trapEditor) return
    if (!trapEditor.draft.name.trim() || !trapEditor.draft.definition.trim()) {
      setError('陷阱名称与定义不能为空')
      return
    }
    setTrapSaving(true)
    setError('')
    try {
      if (trapEditor.id === null) {
        await adminApi.createTrapRule(trapEditor.draft)
      } else {
        await adminApi.updateTrapRule(trapEditor.id, trapEditor.draft)
      }
      setTrapEditor(null)
      setTraps(null)
      const data = await adminApi.listTrapRules()
      setTraps(data.items)
    } catch (caught) {
      handleFailure(caught)
    } finally {
      setTrapSaving(false)
    }
  }

  const stats = vocabPage?.stats ?? { total: 0, enabled: 0, disabled: 0 }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-lg font-bold text-[#26312C]">知识库与熟词僻义管理</h1>
        <p className="mt-1 text-[11px] text-[#8C867B]">
          维护考纲词条、熟词僻义与陷阱规则；修改仅写入本地演示库，学生端即时生效。
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-1.5 border-b border-[#E5DFD3]">
        {[
          { key: 'vocab' as const, label: `词条 ${stats.total.toLocaleString('zh-CN')}` },
          { key: 'traps' as const, label: `陷阱规则 ${traps?.length ?? 8}` },
          { key: 'prompt' as const, label: 'Prompt 版本（原型）' },
        ].map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setTab(item.key)}
            className={`-mb-px border-b-2 px-3 py-2 text-[11px] font-medium transition-colors ${
              tab === item.key
                ? 'border-[#2F6F5E] text-[#2F6F5E]'
                : 'border-transparent text-[#9A948A] hover:text-[#3E4A43]'
            }`}
          >
            {item.label}
          </button>
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

      {tab === 'vocab' ? (
        <section className="rounded-xl border border-[#E5DFD3] bg-white shadow-sm">
          <div className="flex flex-col gap-3 border-b border-[#EDE7DC] px-5 py-3.5 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[10px] text-[#9A948A]">
                启用 <span className="font-semibold text-[#2F6F5E]">{stats.enabled.toLocaleString('zh-CN')}</span>
                {' · '}禁用 <span className="font-semibold text-[#C05746]">{stats.disabled}</span>
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <form
                className="flex items-center gap-1.5 rounded-lg border border-[#E5DFD3] px-2.5"
                onSubmit={(event) => {
                  event.preventDefault()
                  setAppliedKeyword(keyword.trim())
                  setPageIndex(1)
                }}
              >
                <Search className="h-3.5 w-3.5 text-[#B8B1A4]" />
                <input
                  value={keyword}
                  onChange={(event) => setKeyword(event.target.value)}
                  placeholder="单词 / 释义"
                  className="w-32 bg-transparent py-1.5 text-[11px] text-[#3E4A43] outline-none"
                />
              </form>
              <select
                value={level}
                onChange={(event) => {
                  setLevel(event.target.value)
                  setPageIndex(1)
                }}
                className="rounded-lg border border-[#E5DFD3] bg-white px-2 py-1.5 text-[11px] text-[#3E4A43] outline-none"
              >
                {LEVELS.map((item) => (
                  <option key={item || 'all'} value={item}>
                    {item || '全部等级'}
                  </option>
                ))}
              </select>
              <select
                value={enabledFilter}
                onChange={(event) => {
                  setEnabledFilter(event.target.value)
                  setPageIndex(1)
                }}
                className="rounded-lg border border-[#E5DFD3] bg-white px-2 py-1.5 text-[11px] text-[#3E4A43] outline-none"
              >
                <option value="">全部状态</option>
                <option value="1">仅启用</option>
                <option value="0">仅禁用</option>
              </select>
              <button
                type="button"
                onClick={openCreate}
                className="inline-flex items-center gap-1 rounded-lg bg-[#2F6F5E] px-3 py-1.5 text-[11px] font-semibold text-white transition-colors hover:bg-[#275c4e]"
              >
                <Plus className="h-3.5 w-3.5" />
                新增词条
              </button>
            </div>
          </div>

          <div className="hidden grid-cols-[1.1fr_0.7fr_1.4fr_1.6fr_0.5fr_0.6fr_1fr] gap-3 border-b border-[#EDE7DC] bg-[#FCFBF8] px-5 py-2.5 text-[10px] font-medium text-[#9A948A] lg:grid">
            <span>单词</span>
            <span>音标</span>
            <span>基本释义</span>
            <span>熟词僻义</span>
            <span>考频</span>
            <span>等级</span>
            <span className="text-right">操作</span>
          </div>

          {vocabPage?.items.length ? (
            vocabPage.items.map((entry) => (
              <div
                key={entry.id}
                className="flex flex-col gap-2 border-b border-[#EDE7DC] px-5 py-3 last:border-b-0 lg:grid lg:grid-cols-[1.1fr_0.7fr_1.4fr_1.6fr_0.5fr_0.6fr_1fr] lg:items-center lg:gap-3"
              >
                <div className="min-w-0">
                  <p className="text-xs font-semibold text-[#26312C]">
                    {entry.word}
                    {!entry.enabled ? (
                      <span className="ml-1.5 rounded bg-[#FBEDEA] px-1 py-0.5 text-[9px] font-medium text-[#C05746]">
                        已禁用
                      </span>
                    ) : null}
                  </p>
                  <p className="mt-0.5 font-mono text-[10px] text-[#B8B1A4] lg:hidden">
                    {entry.phonetic || '—'}
                  </p>
                </div>
                <span className="hidden font-mono text-[10px] text-[#8C867B] lg:block">
                  {entry.phonetic || '—'}
                </span>
                <span className="truncate text-[11px] text-[#3E4A43]">
                  {entry.basic_meaning}
                </span>
                <span className="truncate text-[11px] text-[#6B6559]">
                  {entry.rare_meaning || '—'}
                </span>
                <span className="text-[11px] tabular-nums text-[#6B6559]">
                  {entry.exam_frequency}
                </span>
                <span>
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium ${
                      LEVEL_TONE[entry.level] ?? 'bg-[#EDE7DC] text-[#6B6559]'
                    }`}
                  >
                    {entry.level}
                  </span>
                </span>
                <div className="flex items-center justify-start gap-1.5 lg:justify-end">
                  <button
                    type="button"
                    onClick={() => openEdit(entry)}
                    className="inline-flex items-center gap-1 rounded-md border border-[#D8D2C6] px-2 py-1.5 text-[10px] font-medium text-[#3E4A43] transition-colors hover:bg-[#F7F4EE]"
                  >
                    <Pencil className="h-3 w-3" />
                    编辑
                  </button>
                  <button
                    type="button"
                    onClick={() => void toggleEntry(entry)}
                    className={`inline-flex items-center gap-1 rounded-md px-2 py-1.5 text-[10px] font-medium transition-colors ${
                      entry.enabled
                        ? 'border border-[#E5DFD3] text-[#6B6559] hover:bg-[#FBEDEA] hover:text-[#C05746]'
                        : 'bg-[#EAF2EE] text-[#2F6F5E] hover:bg-[#DDEBE4]'
                    }`}
                  >
                    <Power className="h-3 w-3" />
                    {entry.enabled ? '禁用' : '启用'}
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="px-5 py-12 text-center text-xs text-[#8C867B]">
              {loading ? '正在读取词库…' : '本地演示库暂无匹配词条'}
            </div>
          )}

          <div className="flex items-center justify-between border-t border-[#EDE7DC] px-5 py-2.5">
            <span className="text-[10px] text-[#9A948A]">
              共 {(vocabPage?.total ?? 0).toLocaleString('zh-CN')} 条 · 第 {vocabPage?.page ?? 1} / {vocabPage?.pages ?? 1} 页
            </span>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                disabled={!vocabPage || vocabPage.page <= 1}
                onClick={() => setPageIndex((index) => Math.max(1, index - 1))}
                className="flex h-6 w-6 items-center justify-center rounded border border-[#E5DFD3] text-[#6B6559] hover:bg-[#F7F4EE] disabled:opacity-40"
              >
                <ChevronLeft className="h-3.5 w-3.5" />
              </button>
              <button
                type="button"
                disabled={!vocabPage || vocabPage.page >= vocabPage.pages}
                onClick={() =>
                  setPageIndex((index) =>
                    vocabPage ? Math.min(vocabPage.pages, index + 1) : index,
                  )
                }
                className="flex h-6 w-6 items-center justify-center rounded border border-[#E5DFD3] text-[#6B6559] hover:bg-[#F7F4EE] disabled:opacity-40"
              >
                <ChevronRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </section>
      ) : null}

      {tab === 'traps' ? (
        <section className="rounded-xl border border-[#E5DFD3] bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-[#EDE7DC] px-5 py-3.5">
            <div className="flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-[#C05746]" strokeWidth={1.8} />
              <span className="text-xs font-semibold text-[#26312C]">选项陷阱规则</span>
            </div>
            <button
              type="button"
              onClick={() =>
                setTrapEditor({
                  id: null,
                  draft: { name: '', definition: '', signals: '', example: '', tone: 'red' },
                })
              }
              className="inline-flex items-center gap-1 rounded-lg border border-[#D8D2C6] px-2.5 py-1.5 text-[10px] font-medium text-[#3E4A43] hover:bg-[#F7F4EE]"
            >
              <Plus className="h-3 w-3" />
              新增规则
            </button>
          </div>
          {traps?.length ? (
            traps.map((rule) => (
              <div
                key={rule.id}
                className="flex flex-col gap-2 border-b border-[#EDE7DC] px-5 py-3.5 last:border-b-0 sm:grid sm:grid-cols-[0.9fr_1.6fr_1fr_0.8fr_auto] sm:items-center sm:gap-3"
              >
                <span className="text-xs font-semibold text-[#26312C]">{rule.name}</span>
                <span className="text-[11px] text-[#3E4A43]">{rule.definition}</span>
                <span className="truncate text-[10px] text-[#8C867B]">{rule.signals || '—'}</span>
                <span className="truncate text-[10px] text-[#8C867B]">{rule.example || '—'}</span>
                <button
                  type="button"
                  onClick={() =>
                    setTrapEditor({
                      id: rule.id,
                      draft: {
                        name: rule.name,
                        definition: rule.definition,
                        signals: rule.signals,
                        example: rule.example,
                        tone: rule.tone,
                      },
                    })
                  }
                  className="inline-flex items-center justify-center gap-1 rounded-md border border-[#D8D2C6] px-2 py-1.5 text-[10px] font-medium text-[#3E4A43] hover:bg-[#F7F4EE]"
                >
                  <Pencil className="h-3 w-3" />
                  编辑
                </button>
              </div>
            ))
          ) : (
            <div className="px-5 py-12 text-center text-xs text-[#8C867B]">
              {traps ? '暂无陷阱规则' : '正在读取陷阱规则…'}
            </div>
          )}
        </section>
      ) : null}

      {tab === 'prompt' ? (
        <section className="rounded-xl border border-[#E5DFD3] bg-white p-6 shadow-sm">
          <div className="flex items-start gap-4">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#EAF2EE] text-[#2F6F5E]">
              <FileJson className="h-5 w-5" strokeWidth={1.8} />
            </span>
            <div>
              <p className="text-sm font-bold text-[#26312C]">Prompt 版本（原型）</p>
              <p className="mt-1 text-[11px] leading-relaxed text-[#8C867B]">
                该页签在原型中用于查看各工作流的 Prompt 版本与变更记录。当前实现把
                Prompt 放在服务端代码里，版本化留待后续迭代。
              </p>
              <p className="mt-3 text-[10px] text-[#9A948A]">
                数据来源：server/workflows.py · server/llm.py
              </p>
            </div>
          </div>
        </section>
      ) : null}

      <p className="text-[10px] text-[#9A948A]">
        数据来源：syllabus_vocabulary / trap_rules / exam_sentences
      </p>

      {drawer ? (
        <>
          <div
            className="fixed inset-0 z-40 bg-[#26312C]/30"
            onClick={() => setDrawer(null)}
            aria-hidden
          />
          <aside className="fixed inset-y-0 right-0 z-50 flex w-full max-w-[456px] flex-col border-l border-[#E5DFD3] bg-white shadow-2xl">
            <div className="flex items-start justify-between gap-3 border-b border-[#EDE7DC] px-5 py-4">
              <div>
                <p className="text-[10px] uppercase tracking-[0.16em] text-[#9A948A]">
                  词条管理 / 本地编辑
                </p>
                <p className="mt-1 text-sm font-bold text-[#26312C]">
                  {drawer.mode === 'create' ? '新增词条' : `编辑词条 · ${drawer.draft.word}`}
                </p>
                <p className="mt-0.5 flex items-center gap-1 text-[10px] text-[#8C867B]">
                  <History className="h-3 w-3" />
                  本地词条 · 修改仅写入演示库
                </p>
              </div>
              <button
                type="button"
                aria-label="关闭抽屉"
                onClick={() => setDrawer(null)}
                className="rounded-lg p-1.5 text-[#9A948A] transition-colors hover:bg-[#F7F4EE] hover:text-[#26312C]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex-1 space-y-3 overflow-y-auto px-5 py-4">
              {[
                { key: 'word' as const, label: '单词', readonly: drawer.mode === 'edit' },
                { key: 'phonetic' as const, label: '音标', readonly: false },
                { key: 'basic_meaning' as const, label: '基本释义', readonly: false },
                { key: 'rare_meaning' as const, label: '熟词僻义', readonly: false },
              ].map(({ key, label, readonly }) => (
                <label key={key} className="block">
                  <span className="text-[11px] font-medium text-[#3E4A43]">{label}</span>
                  <input
                    value={drawer.draft[key]}
                    readOnly={readonly}
                    onChange={(event) =>
                      setDrawer((current) =>
                        current
                          ? {
                              ...current,
                              draft: { ...current.draft, [key]: event.target.value },
                            }
                          : current,
                      )
                    }
                    className={`mt-1.5 w-full rounded-lg border border-[#D8D2C6] px-3 py-2 text-xs outline-none focus:border-[#2F6F5E] ${
                      readonly ? 'bg-[#F7F4EE] text-[#8C867B]' : 'text-[#26312C]'
                    }`}
                  />
                </label>
              ))}
              <div className="grid grid-cols-2 gap-3">
                <label className="block">
                  <span className="text-[11px] font-medium text-[#3E4A43]">等级</span>
                  <select
                    value={drawer.draft.level}
                    onChange={(event) =>
                      setDrawer((current) =>
                        current
                          ? {
                              ...current,
                              draft: { ...current.draft, level: event.target.value },
                            }
                          : current,
                      )
                    }
                    className="mt-1.5 w-full rounded-lg border border-[#D8D2C6] bg-white px-3 py-2 text-xs text-[#26312C] outline-none focus:border-[#2F6F5E]"
                  >
                    {LEVELS.filter(Boolean).map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block">
                  <span className="text-[11px] font-medium text-[#3E4A43]">考频</span>
                  <input
                    type="number"
                    min={0}
                    max={999}
                    value={drawer.draft.exam_frequency}
                    onChange={(event) =>
                      setDrawer((current) =>
                        current
                          ? {
                              ...current,
                              draft: {
                                ...current.draft,
                                exam_frequency: Number(event.target.value),
                              },
                            }
                          : current,
                      )
                    }
                    className="mt-1.5 w-full rounded-lg border border-[#D8D2C6] px-3 py-2 text-xs text-[#26312C] outline-none focus:border-[#2F6F5E]"
                  />
                </label>
              </div>

              <div className="pt-1">
                <div className="flex items-center gap-2">
                  <LibraryBig className="h-3.5 w-3.5 text-[#2F6F5E]" />
                  <span className="text-[11px] font-semibold text-[#26312C]">
                    关联真题切片（{drawer.citations.length}）
                  </span>
                </div>
                {drawer.loading ? (
                  <p className="mt-2 flex items-center gap-1.5 text-[10px] text-[#9A948A]">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    正在检索发布篇章…
                  </p>
                ) : drawer.citations.length ? (
                  <ul className="mt-2 space-y-2">
                    {drawer.citations.map((citation) => (
                      <li
                        key={citation.sentence_id}
                        className="rounded-lg border border-[#EDE7DC] bg-[#FCFBF8] px-3 py-2.5"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <span className="text-[10px] font-semibold text-[#3E4A43]">
                            {citation.source}
                          </span>
                          {citation.question_type ? (
                            <span className="rounded bg-[#EAF2EE] px-1.5 py-0.5 text-[9px] font-medium text-[#2F6F5E]">
                              {citation.question_type}
                            </span>
                          ) : null}
                        </div>
                        <p className="mt-1.5 text-[10px] leading-relaxed text-[#6B6559]">
                          …{citation.text.slice(0, 120)}
                          {citation.text.length > 120 ? '…' : ''}
                        </p>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-2 rounded-lg border border-dashed border-[#E5DFD3] px-3 py-3 text-[10px] text-[#B8B1A4]">
                    发布篇章中暂无包含该词的句子。
                  </p>
                )}
              </div>
            </div>

            <div className="border-t border-[#EDE7DC] px-5 py-3.5">
              <p className="mb-2.5 flex items-center gap-1 text-[10px] text-[#9A948A]">
                <CheckCircle2 className="h-3 w-3 text-[#2F6F5E]" />
                仅写入本地演示库
              </p>
              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setDrawer(null)}
                  className="rounded-lg border border-[#D8D2C6] px-3.5 py-2 text-[11px] font-medium text-[#6B6559] transition-colors hover:bg-[#F7F4EE]"
                >
                  取消
                </button>
                <button
                  type="button"
                  onClick={() => void saveDrawer()}
                  disabled={saving}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-[#2F6F5E] px-3.5 py-2 text-[11px] font-semibold text-white transition-colors hover:bg-[#275c4e] disabled:opacity-60"
                >
                  {saving ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <Save className="h-3.5 w-3.5" />
                  )}
                  {saving ? '保存中…' : '保存'}
                </button>
              </div>
            </div>
          </aside>
        </>
      ) : null}

      {trapEditor ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#26312C]/40 px-4">
          <div className="w-full max-w-md rounded-xl border border-[#E5DFD3] bg-white p-5 shadow-xl">
            <div className="flex items-center justify-between">
              <p className="text-sm font-bold text-[#26312C]">
                {trapEditor.id === null ? '新增陷阱规则' : '编辑陷阱规则'}
              </p>
              <button
                type="button"
                aria-label="关闭"
                onClick={() => setTrapEditor(null)}
                className="rounded p-1 text-[#9A948A] hover:bg-[#F7F4EE] hover:text-[#26312C]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="mt-3 space-y-3">
              {[
                { key: 'name' as const, label: '名称' },
                { key: 'definition' as const, label: '定义' },
                { key: 'signals' as const, label: '识别信号' },
                { key: 'example' as const, label: '示例' },
              ].map(({ key, label }) => (
                <label key={key} className="block">
                  <span className="text-[11px] font-medium text-[#3E4A43]">{label}</span>
                  <input
                    value={trapEditor.draft[key]}
                    onChange={(event) =>
                      setTrapEditor((current) =>
                        current
                          ? {
                              ...current,
                              draft: { ...current.draft, [key]: event.target.value },
                            }
                          : current,
                      )
                    }
                    className="mt-1.5 w-full rounded-lg border border-[#D8D2C6] px-3 py-2 text-xs text-[#26312C] outline-none focus:border-[#2F6F5E]"
                  />
                </label>
              ))}
              <label className="block">
                <span className="text-[11px] font-medium text-[#3E4A43]">色调</span>
                <select
                  value={trapEditor.draft.tone}
                  onChange={(event) =>
                    setTrapEditor((current) =>
                      current
                        ? {
                            ...current,
                            draft: { ...current.draft, tone: event.target.value },
                          }
                        : current,
                    )
                  }
                  className="mt-1.5 w-full rounded-lg border border-[#D8D2C6] bg-white px-3 py-2 text-xs text-[#26312C] outline-none focus:border-[#2F6F5E]"
                >
                  <option value="red">red</option>
                  <option value="amber">amber</option>
                  <option value="emerald">emerald</option>
                  <option value="violet">violet</option>
                </select>
              </label>
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setTrapEditor(null)}
                className="rounded-lg border border-[#D8D2C6] px-3 py-1.5 text-[11px] font-medium text-[#6B6559] hover:bg-[#F7F4EE]"
              >
                取消
              </button>
              <button
                type="button"
                onClick={() => void saveTrap()}
                disabled={trapSaving}
                className="inline-flex items-center gap-1.5 rounded-lg bg-[#2F6F5E] px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-[#275c4e] disabled:opacity-60"
              >
                {trapSaving ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Save className="h-3.5 w-3.5" />
                )}
                保存
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}