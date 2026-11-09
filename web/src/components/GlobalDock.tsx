import { useEffect, useState } from 'react'
import type { LucideIcon } from 'lucide-react'
import {
  BarChart3,
  BookMarked,
  CalendarCheck,
  MessageSquareText,
  Sparkles,
  X,
} from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { api, type InsightsResponse } from '../lib/api'
import { useAppStore } from '../store/AppStore'

interface DockEntry {
  to: string
  label: string
  hint: string
  icon: LucideIcon
  badge: number
}

export function GlobalDock() {
  const [open, setOpen] = useState(false)
  const [insights, setInsights] = useState<InsightsResponse | null>(null)
  const { pathname } = useLocation()
  const { dueWords } = useAppStore()

  useEffect(() => {
    let alive = true
    api
      .getInsights()
      .then((data) => {
        if (alive) setInsights(data)
      })
      .catch(() => {
        // The dock is an enhancement; keep the app usable offline.
      })
    return () => {
      alive = false
    }
  }, [pathname, open])

  useEffect(() => {
    if (!open) return
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [open])

  const pendingToday = insights?.today_tasks.length ?? 0
  const dueCount = insights?.due_word_count ?? dueWords.length
  const busy = pendingToday + dueCount

  const entries: DockEntry[] = [
    {
      to: '/chat',
      label: '问 Agent',
      hint: '开口即问，工具先查证',
      icon: MessageSquareText,
      badge: 0,
    },
    {
      to: '/plan',
      label: '今日计划',
      hint: pendingToday > 0 ? `${pendingToday} 项待完成` : '按薄弱项自动排程',
      icon: CalendarCheck,
      badge: pendingToday,
    },
    {
      to: '/wordbook',
      label: '待复习',
      hint: dueCount > 0 ? `${dueCount} 个单词到期` : '今天没有到期单词',
      icon: BookMarked,
      badge: dueCount,
    },
    {
      to: '/report',
      label: '学习报告',
      hint: '正确率与薄弱题型',
      icon: BarChart3,
      badge: 0,
    },
  ]

  return (
    <div className="fixed bottom-5 right-4 z-50 sm:bottom-6 sm:right-6">
      {open ? (
        <div
          role="menu"
          aria-label="全局快捷入口"
          className="absolute bottom-16 right-0 w-64 rounded-xl border border-slate-200 bg-white p-2 shadow-xl shadow-slate-900/10"
        >
          <div className="flex items-center justify-between px-2.5 pb-1.5 pt-1">
            <span className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
              全局快捷
            </span>
            {busy > 0 ? (
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600">
                {busy} 项待办
              </span>
            ) : null}
          </div>
          {entries.map(({ to, label, hint, icon: Icon, badge }) => (
            <Link
              key={to}
              to={to}
              role="menuitem"
              onClick={() => setOpen(false)}
              className="flex items-center gap-3 rounded-lg px-2.5 py-2.5 transition-colors hover:bg-slate-50"
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-600">
                <Icon className="h-4 w-4" strokeWidth={1.8} />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-xs font-semibold text-slate-800">
                  {label}
                </span>
                <span className="mt-0.5 block truncate text-[10px] text-slate-400">
                  {hint}
                </span>
              </span>
              {badge > 0 ? (
                <span className="flex h-5 min-w-5 shrink-0 items-center justify-center rounded-full bg-red-500 px-1.5 text-[10px] font-bold text-white">
                  {badge > 99 ? '99+' : badge}
                </span>
              ) : null}
            </Link>
          ))}
        </div>
      ) : null}

      <button
        type="button"
        aria-label={open ? '收起全局快捷面板' : '打开全局快捷面板'}
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => setOpen((value) => !value)}
        className={`relative flex items-center gap-2 rounded-full bg-slate-900 text-white shadow-lg shadow-slate-900/20 transition-all hover:bg-slate-800 ${
          open ? 'h-12 w-12 justify-center px-0' : 'h-12 pl-4 pr-5'
        }`}
      >
        {open ? (
          <X className="h-5 w-5" />
        ) : (
          <>
            <Sparkles className="h-5 w-5" strokeWidth={1.8} />
            <span className="text-xs font-semibold">快捷</span>
            {busy > 0 ? (
              <span className="absolute -right-0.5 -top-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
                {busy > 99 ? '99+' : busy}
              </span>
            ) : null}
          </>
        )}
      </button>
    </div>
  )
}