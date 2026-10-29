import { useEffect, useRef, useState } from 'react'
import {
  BookMarked,
  BookOpen,
  ChevronRight,
  Grid2X2,
  Home,
  MapPin,
  ScanText,
  Target,
  Trash2,
} from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'
import { api, type PassageSummary } from '../lib/api'
import { ContentLibraryDrawer } from './ContentLibraryDrawer'
import { useSession } from '../store/SessionStore'
import { useWorkspace } from '../store/WorkspaceStore'

const VIEW_LABELS: Record<string, string> = {
  '/': 'Agent 中枢',
  '/studio': '全粒度精析',
  '/reading': '阅读实战',
  '/vocab': '记忆舱',
}

const MANUAL_LINKS = [
  { to: '/studio', label: '全粒度精析', hint: '词 / 句 / 段 / 篇', icon: ScanText },
  { to: '/reading', label: '阅读实战训练场', hint: '左文右题与陷阱验伪', icon: Target },
  { to: '/vocab', label: '艾宾浩斯记忆舱', hint: 'SM-2 闪卡与语境', icon: BookMarked },
]

function ManualRoam() {
  const { context, updateContext } = useWorkspace()
  const { clearMessages } = useSession()
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [passages, setPassages] = useState<PassageSummary[]>([])
  const [libraryOpen, setLibraryOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const close = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', close)
    return () => document.removeEventListener('mousedown', close)
  }, [open])

  useEffect(() => {
    if (!open || passages.length) return
    api
      .getPassages()
      .then((response) => setPassages(response.items.slice(0, 8)))
      .catch(() => setPassages([]))
  }, [open, passages.length])

  const go = (to: string) => {
    setOpen(false)
    updateContext({
      active_passage_id: null,
      active_passage_label: null,
      active_question_id: null,
      active_sentence_id: null,
      selected_raw_text: null,
    })
    navigate(to)
  }

  const label = VIEW_LABELS[pathname] ?? 'Agent 中枢'
  const bound = context.active_passage_label
    ? `已绑定：${context.active_passage_label}`
    : context.active_passage_id
      ? `已绑定：${context.active_passage_id.slice(0, 12)}`
      : '未绑定画布'
  const stageLabel =
    pathname !== '/' &&
    pathname !== '/dashboard' &&
    context.active_passage_label &&
    !context.active_passage_label.startsWith('自定义')
      ? `${label} · ${context.active_passage_label}`
      : label

  return (
    <>
    <header className="relative z-30 flex h-12 shrink-0 items-center justify-between gap-3 border-b border-slate-200 bg-white/90 px-3 backdrop-blur">
      <div ref={rootRef} className="relative flex min-w-0 items-center gap-2">
        <button
          type="button"
          onClick={() => go('/')}
          aria-label="返回首页"
          title="返回首页"
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 hover:bg-slate-50 hover:text-slate-900"
        >
          <Home className="h-3.5 w-3.5" />
        </button>
        <button
          type="button"
          onClick={() => setOpen((prev) => !prev)}
          className="inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 text-[11px] font-medium text-slate-600 hover:bg-slate-50"
        >
          <Grid2X2 className="h-3.5 w-3.5" />
          手动漫游
        </button>
        <span className="truncate text-[10px] text-slate-400">{stageLabel}</span>

        {open ? (
          <div className="absolute left-0 top-10 w-[min(560px,calc(100vw-1.5rem))] overflow-hidden rounded-xl border border-slate-200 bg-white/95 shadow-2xl shadow-slate-900/10 backdrop-blur-xl">
            <div className="border-b border-slate-100 px-3.5 py-2.5">
              <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
                手动漫游
              </p>
              <p className="mt-0.5 text-[10px] text-slate-400">
                不占用常驻空间，选择后直接进入对应画布。
              </p>
            </div>
            <div className="grid grid-cols-1 gap-1 p-2 sm:grid-cols-2">
              {MANUAL_LINKS.map((item) => (
                <button
                  key={item.to}
                  type="button"
                  onClick={() => go(item.to)}
                  className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-left hover:bg-slate-50"
                >
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-600">
                    <item.icon className="h-3.5 w-3.5" />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-[11px] font-medium text-slate-700">
                      {item.label}
                    </span>
                    <span className="block text-[9px] text-slate-400">{item.hint}</span>
                  </span>
                  <ChevronRight className="h-3 w-3 shrink-0 text-slate-300" />
                </button>
              ))}
            </div>

            <div className="border-t border-slate-100 p-2">
              <p className="px-1 pb-1.5 text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                手动选文章
              </p>
              <div className="grid max-h-44 grid-cols-1 gap-1 overflow-y-auto sm:grid-cols-2">
                {passages.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() =>
                      go(
                        `/reading?year=${item.year}&exam=${encodeURIComponent(item.exam_type)}&text=${item.text_number}`,
                      )
                    }
                    className="flex items-center justify-between gap-2 rounded-md px-2 py-1.5 text-left text-[10px] text-slate-600 hover:bg-slate-50"
                  >
                    <span className="truncate">
                      {item.year} {item.exam_type} · Text {item.text_number}
                    </span>
                    <span className="shrink-0 text-[9px] text-slate-400">
                      {item.question_count} 题
                    </span>
                  </button>
                ))}
                {!passages.length ? (
                  <p className="px-2 py-2 text-[10px] text-slate-400">
                    暂无可选已发布文章
                  </p>
                ) : null}
              </div>
              <p className="mt-1 px-2 text-[9px] text-slate-400">
                题库导入与发布已收进 Agent 工具链，不再占用主导航。
              </p>
              <button
                type="button"
                onClick={() => { setOpen(false); setLibraryOpen(true) }}
                className="mt-2 flex w-full items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 py-2 text-left text-[10px] font-medium text-slate-600 hover:bg-slate-50"
              >
                <BookOpen className="h-3.5 w-3.5 text-cyan-600" />
                内容库 · 导入泛读文章
              </button>
            </div>
          </div>
        ) : null}
      </div>

      <div className="flex shrink-0 items-center gap-1.5">
        <span className="hidden items-center gap-1 rounded-full bg-slate-50 px-2.5 py-1 text-[9px] font-medium text-slate-500 ring-1 ring-slate-100 sm:flex">
          <MapPin className="h-2.5 w-2.5 text-emerald-500" />
          {bound}
        </span>
        <button
          type="button"
          onClick={clearMessages}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700"
          title="清空会话"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
    </header>
    <ContentLibraryDrawer open={libraryOpen} onClose={() => setLibraryOpen(false)} />
    </>
  )
}

export function OSTopbar() {
  return <ManualRoam />
}
