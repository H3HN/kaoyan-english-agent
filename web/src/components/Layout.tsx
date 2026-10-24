import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'
import {
  BarChart3,
  BookMarked,
  BookOpenCheck,
  Layers,
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

type NavTone = 'home' | 'feature' | 'default'

type NavItem = {
  to: string
  label: string
  icon: LucideIcon
  end?: boolean
  tone?: NavTone
}

const navItems: NavItem[] = [
  { to: '/', label: '首页', icon: LayoutDashboard, end: true, tone: 'home' },
  { to: '/sentence', label: '长难句拆解', icon: ScanText, tone: 'feature' },
  { to: '/options', label: '阅读真题训练', icon: Target, tone: 'feature' },
  { to: '/chat', label: 'AI 对话', icon: MessageSquareText, tone: 'feature' },
  { to: '/wordbook', label: '我的单词本', icon: BookMarked, tone: 'feature' },
  { to: '/library', label: '资料库', icon: Layers },
  { to: '/report', label: '学习报告', icon: BarChart3 },
  { to: '/knowledge', label: '领域知识库', icon: LibraryBig },
]

const pageTitles: Record<string, string> = {
  '/': '研英智学 · 考研英语 Agent',
  '/sentence': '长难句拆解 · 研英智学',
  '/options': '阅读真题训练 · 研英智学',
  '/library': '资料库 · 研英智学',
  '/chat': 'AI 对话 · 研英智学',
  '/wordbook': '我的单词本 · 研英智学',
  '/report': '学习报告 · 研英智学',
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
        <nav className="mt-2 space-y-1.5" aria-label="主导航">
          {navItems.map(({ to, label, icon: Icon, end, tone }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onNavigate}
              className={({ isActive }) => {
                const base =
                  'group flex items-center gap-3 rounded-lg transition-colors'
                if (tone === 'home') {
                  return `${base} px-3.5 py-3.5 text-[15px] font-bold shadow-sm ${
                    isActive
                      ? 'bg-slate-900 text-white'
                      : 'border border-slate-200 bg-white text-slate-900 hover:border-slate-300 hover:bg-slate-50'
                  }`
                }
                if (tone === 'feature') {
                  return `${base} border px-3 py-2.5 text-[13px] font-semibold shadow-sm ${
                    isActive
                      ? 'border-amber-600 bg-amber-600 text-white'
                      : 'border-slate-200 bg-white text-amber-600 hover:bg-amber-50/70 hover:text-amber-700'
                  }`
                }
                return `${base} border border-slate-200 px-3 py-2.5 text-[13px] shadow-sm ${
                  isActive
                    ? 'bg-slate-100 font-semibold text-slate-900'
                    : 'bg-white font-medium text-slate-500 hover:bg-slate-50 hover:text-slate-800'
                }`
              }}
            >
              {({ isActive }) => (
                <>
                  <Icon
                    className={`shrink-0 ${
                      tone === 'home' ? 'h-5 w-5' : 'h-[18px] w-[18px]'
                    } ${
                      tone === 'home'
                        ? isActive
                          ? 'text-white'
                          : 'text-slate-700'
                        : tone === 'feature'
                          ? isActive
                            ? 'text-white'
                            : 'text-amber-600'
                          : isActive
                            ? 'text-slate-800'
                            : 'text-slate-400 group-hover:text-slate-600'
                    }`}
                    strokeWidth={tone === 'home' ? 2 : 1.8}
                  />
                  <span className="min-w-0 flex-1 truncate">{label}</span>
                  {isActive ? (
                    <span
                      className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                        tone === 'home'
                          ? 'bg-white'
                          : tone === 'feature'
                            ? 'bg-white'
                            : 'bg-slate-800'
                      }`}
                    />
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
