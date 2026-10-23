import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import {
  BarChart3,
  BookMarked,
  BookOpenCheck,
  GitCompareArrows,
  LayoutDashboard,
  LibraryBig,
  Menu,
  MessageSquareText,
  ScanText,
  Target,
  X,
} from 'lucide-react'
import { Link, NavLink, useLocation } from 'react-router-dom'
import { useAppStore } from '../store/AppStore'

const navItems = [
  { to: '/', label: '首页', icon: LayoutDashboard, end: true },
  { to: '/sentence', label: '长难句拆解', icon: ScanText },
  { to: '/options', label: '选项陷阱分析', icon: Target },
  { to: '/chat', label: 'AI 对话', icon: MessageSquareText },
  { to: '/wordbook', label: '单词本与复习', icon: BookMarked },
  { to: '/report', label: '学习报告', icon: BarChart3 },
  { to: '/comparison', label: '定制对比', icon: GitCompareArrows },
  { to: '/knowledge', label: '领域知识库', icon: LibraryBig },
]

const pageTitles: Record<string, string> = {
  '/': '研英智学 · 考研英语 Agent',
  '/sentence': '长难句拆解 · 研英智学',
  '/options': '选项陷阱分析 · 研英智学',
  '/chat': 'AI 对话 · 研英智学',
  '/wordbook': '单词本与复习 · 研英智学',
  '/report': '学习报告 · 研英智学',
  '/comparison': '定制效果对比 · 研英智学',
  '/knowledge': '领域知识库 · 研英智学',
}

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [pathname])
  useEffect(() => {
    document.title = pageTitles[pathname] ?? '研英智学'
  }, [pathname])
  return null
}

function SidebarContent({
  onNavigate,
  connected,
}: {
  onNavigate?: () => void
  connected: boolean
}) {
  return (
    <div className="flex h-full flex-col px-4 py-6">
      <Link
        to="/"
        onClick={onNavigate}
        className="flex items-center gap-3 rounded-lg px-1 py-1"
      >
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-800 text-white shadow-sm">
          <BookOpenCheck className="h-5 w-5" strokeWidth={1.8} />
        </span>
        <span className="min-w-0">
          <span className="block text-[15px] font-bold tracking-tight text-slate-900">
            研英智学
          </span>
          <span className="mt-0.5 block text-[9px] font-medium uppercase tracking-[0.16em] text-slate-400">
            Academic Studio
          </span>
        </span>
      </Link>

      <div className="mt-5 rounded-lg border border-slate-200 bg-slate-50/80 px-3 py-2.5">
        <div className="flex items-center justify-between gap-2">
          <span className="text-[11px] text-slate-500">服务状态</span>
          <span
            className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[10px] font-medium ${
              connected
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-amber-50 text-amber-700'
            }`}
          >
            <span
              className={`h-1.5 w-1.5 rounded-full ${
                connected ? 'bg-emerald-500' : 'bg-amber-500'
              }`}
            />
            {connected ? '已连接' : '本地模式'}
          </span>
        </div>
        <p className="mt-1.5 text-[10px] leading-relaxed text-slate-400">
          {connected
            ? 'SQLite · FastAPI · 领域知识库'
            : '本地演示数据 · 启动后端后同步'}
        </p>
      </div>

      <div className="mt-7">
        <p className="px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
          学习工作台
        </p>
        <nav className="mt-2 space-y-0.5" aria-label="主导航">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onNavigate}
              className={({ isActive }) =>
                `group flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] transition-colors ${
                  isActive
                    ? 'bg-slate-100 font-semibold text-slate-900'
                    : 'font-medium text-slate-500 hover:bg-slate-50 hover:text-slate-800'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={`h-[18px] w-[18px] shrink-0 ${
                      isActive
                        ? 'text-slate-800'
                        : 'text-slate-400 group-hover:text-slate-600'
                    }`}
                    strokeWidth={1.8}
                  />
                  <span className="min-w-0 flex-1 truncate">{label}</span>
                  {isActive ? (
                    <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-slate-800" />
                  ) : null}
                </>
              )}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="mt-auto pt-6">
        <div className="border-t border-slate-200 pt-4">
          <p className="text-[11px] text-slate-500">福大智联 · 2026 秋</p>
          <p className="mt-1 text-[10px] text-slate-400">v0.3.0 · 前后端分离</p>
        </div>
      </div>
    </div>
  )
}

export function Layout({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const { pathname } = useLocation()
  const { connected } = useAppStore()

  useEffect(() => {
    setOpen(false)
  }, [pathname])

  useEffect(() => {
    if (!open) return
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previous
    }
  }, [open])

  return (
    <div className="min-h-screen bg-slate-50">
      <ScrollToTop />

      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[240px] border-r border-slate-200 bg-white lg:block">
        <SidebarContent connected={connected} />
      </aside>

      {open ? (
        <button
          type="button"
          aria-label="关闭导航"
          onClick={() => setOpen(false)}
          className="fixed inset-0 z-30 bg-slate-900/30 backdrop-blur-[2px] lg:hidden"
        />
      ) : null}

      <aside
        className={`fixed inset-y-0 left-0 z-40 w-[240px] border-r border-slate-200 bg-white transition-transform duration-200 lg:hidden ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <button
          type="button"
          aria-label="关闭导航"
          onClick={() => setOpen(false)}
          className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-700"
        >
          <X className="h-4 w-4" />
        </button>
        <SidebarContent
          connected={connected}
          onNavigate={() => setOpen(false)}
        />
      </aside>

      <div className="lg:pl-[240px]">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-slate-200 bg-white/90 px-4 backdrop-blur lg:hidden">
          <Link to="/" className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-800 text-white">
              <BookOpenCheck className="h-4 w-4" />
            </span>
            <span className="text-sm font-bold text-slate-900">研英智学</span>
          </Link>
          <button
            type="button"
            aria-label="打开导航"
            onClick={() => setOpen(true)}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50"
          >
            <Menu className="h-4 w-4" />
          </button>
        </header>

        <main className="mx-auto w-full max-w-[1240px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          {children}
        </main>
      </div>
    </div>
  )
}
