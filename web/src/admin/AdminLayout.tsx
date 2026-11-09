import { createContext, useContext, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'
import {
  BookOpenCheck,
  ClipboardList,
  LibraryBig,
  LineChart,
  LockKeyhole,
  LogOut,
  ShieldCheck,
} from 'lucide-react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import {
  AdminAuthError,
  adminApi,
  clearAdminToken,
  getAdminToken,
  setAdminToken,
} from '../lib/adminApi'

interface AdminAuthValue {
  lock: () => void
}

export const AdminAuthContext = createContext<AdminAuthValue>({ lock: () => {} })

export function useAdminAuth() {
  return useContext(AdminAuthContext)
}

interface NavItem {
  to: string
  label: string
  hint: string
  icon: LucideIcon
}

const navItems: NavItem[] = [
  {
    to: '/admin/workbench',
    label: '题库导入工作台',
    hint: '导入 · 审核 · 发布 · 撤回',
    icon: ClipboardList,
  },
  {
    to: '/admin/knowledge',
    label: '知识库',
    hint: '词条 · 陷阱规则',
    icon: LibraryBig,
  },
  {
    to: '/admin/monitor',
    label: '运行监控',
    hint: 'Agent 运行与学情',
    icon: LineChart,
  },
]

const pageTitles: Record<string, string> = {
  '/admin/workbench': '题库导入工作台',
  '/admin/knowledge': '知识库与熟词僻义管理',
  '/admin/monitor': '运行监控与学情看板',
}

export default function AdminLayout() {
  const [unlocked, setUnlocked] = useState(() => Boolean(getAdminToken()))
  const [tokenInput, setTokenInput] = useState('')
  const [checking, setChecking] = useState(false)
  const [error, setError] = useState('')
  const { pathname } = useLocation()

  useEffect(() => {
    document.title = `${pageTitles[pathname] ?? '内容管理台'} · 研英智学管理端`
  }, [pathname])

  const lock = () => {
    clearAdminToken()
    setUnlocked(false)
    setTokenInput('')
  }

  const unlock = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const value = tokenInput.trim()
    if (!value) {
      setError('请输入管理员令牌')
      return
    }
    setChecking(true)
    setError('')
    setAdminToken(value)
    try {
      await adminApi.getStats()
      setUnlocked(true)
    } catch (caught) {
      clearAdminToken()
      setError(
        caught instanceof AdminAuthError
          ? '令牌无效，请核对 server/.env 中的 ADMIN_TOKEN'
          : '无法连接后端，请确认 FastAPI 已启动',
      )
    } finally {
      setChecking(false)
    }
  }

  if (!unlocked) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#1F4E43] px-4">
        <form
          onSubmit={unlock}
          className="w-full max-w-sm rounded-2xl border border-white/10 bg-[#F7F4EE] p-7 shadow-2xl"
        >
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#1F4E43] text-white">
              <ShieldCheck className="h-5 w-5" strokeWidth={1.8} />
            </span>
            <div>
              <p className="text-sm font-bold text-[#26312C]">内容管理台</p>
              <p className="text-[10px] tracking-[0.16em] text-[#9A948A]">
                ADMIN CONSOLE
              </p>
            </div>
          </div>
          <p className="mt-5 text-[11px] leading-relaxed text-[#8C867B]">
            输入管理员令牌解锁题库导入、知识库编辑与运行监控。令牌来自
            <code className="mx-1 rounded bg-[#EDE7DC] px-1 py-0.5 text-[10px]">
              server/.env
            </code>
            中的 <code className="text-[10px]">ADMIN_TOKEN</code>，本地演示默认
            <code className="mx-1 rounded bg-[#EDE7DC] px-1 py-0.5 text-[10px]">
              dev-admin
            </code>
            。
          </p>
          <label className="mt-4 block">
            <span className="text-[11px] font-medium text-[#3E4A43]">管理员令牌</span>
            <div className="mt-1.5 flex items-center gap-2 rounded-lg border border-[#D8D2C6] bg-white px-3">
              <LockKeyhole className="h-4 w-4 shrink-0 text-[#9A948A]" />
              <input
                type="password"
                value={tokenInput}
                onChange={(event) => setTokenInput(event.target.value)}
                placeholder="dev-admin"
                className="w-full bg-transparent py-2.5 text-xs text-[#26312C] outline-none"
              />
            </div>
          </label>
          {error ? (
            <p className="mt-3 rounded-lg bg-[#FBEDEA] px-3 py-2 text-[11px] text-[#C05746]">
              {error}
            </p>
          ) : null}
          <button
            type="submit"
            disabled={checking}
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-[#2F6F5E] px-4 py-2.5 text-xs font-semibold text-white transition-colors hover:bg-[#275c4e] disabled:opacity-60"
          >
            <ShieldCheck className="h-4 w-4" />
            {checking ? '正在解锁…' : '解 锁'}
          </button>
          <Link
            to="/"
            className="mt-3 block text-center text-[10px] text-[#9A948A] hover:text-[#3E4A43]"
          >
            返回学生端
          </Link>
        </form>
      </div>
    )
  }

  return (
    <AdminAuthContext.Provider value={{ lock }}>
      <div className="min-h-screen bg-[#F4F1EC]">
        <aside className="fixed inset-y-0 left-0 z-40 hidden w-[240px] bg-[#1F4E43] lg:block">
          <div className="flex h-full flex-col px-4 py-6">
            <Link to="/admin/workbench" className="flex items-center gap-3 px-1">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/10 text-white">
                <BookOpenCheck className="h-5 w-5" strokeWidth={1.8} />
              </span>
              <span className="min-w-0">
                <span className="block text-[15px] font-bold tracking-tight text-white">
                  研英智学
                </span>
                <span className="mt-0.5 block text-[9px] font-medium uppercase tracking-[0.16em] text-white/50">
                  Content Console
                </span>
              </span>
            </Link>

            <nav className="mt-7 space-y-1.5" aria-label="内容管理台导航">
              {navItems.map(({ to, label, hint, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `flex items-start gap-3 rounded-lg px-3 py-2.5 transition-colors ${
                      isActive
                        ? 'bg-white/12 text-white'
                        : 'text-white/65 hover:bg-white/8 hover:text-white'
                    }`
                  }
                >
                  <Icon className="mt-0.5 h-[18px] w-[18px] shrink-0" strokeWidth={1.8} />
                  <span className="min-w-0">
                    <span className="block text-[13px] font-semibold">{label}</span>
                    <span className="mt-0.5 block truncate text-[10px] text-white/40">
                      {hint}
                    </span>
                  </span>
                </NavLink>
              ))}
            </nav>

            <div className="mt-auto space-y-3 pt-6">
              <div className="rounded-lg bg-black/15 px-3 py-2.5">
                <p className="text-[10px] text-white/45">本地演示库</p>
                <p className="mt-0.5 text-[10px] text-white/35">v1.1 · 单管理员</p>
              </div>
              <Link
                to="/"
                className="flex items-center gap-2 rounded-lg px-3 py-2 text-[11px] text-white/50 transition-colors hover:bg-white/8 hover:text-white"
              >
                <LogOut className="h-3.5 w-3.5" />
                返回学生端
              </Link>
            </div>
          </div>
        </aside>

        <div className="lg:pl-[240px]">
          <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-3 border-b border-[#E5DFD3] bg-white px-4 sm:px-6">
            <div className="flex min-w-0 items-center gap-2.5">
              <span className="hidden text-[11px] text-[#9A948A] sm:inline">
                研英智学 /
              </span>
              <span className="truncate text-sm font-semibold text-[#26312C]">
                {pageTitles[pathname] ?? '内容管理台'}
              </span>
              <span className="hidden rounded-full bg-[#EAF2EE] px-2 py-0.5 text-[10px] font-medium text-[#2F6F5E] sm:inline">
                本地演示库
              </span>
            </div>
            <div className="flex shrink-0 items-center gap-2.5">
              <span className="hidden items-center gap-1.5 text-[11px] font-medium text-[#2F6F5E] sm:flex">
                <span className="h-1.5 w-1.5 rounded-full bg-[#2F6F5E]" />
                管理员已解锁
              </span>
              <button
                type="button"
                onClick={lock}
                className="inline-flex items-center gap-1.5 rounded-lg border border-[#E5DFD3] px-2.5 py-1.5 text-[11px] text-[#6B6559] transition-colors hover:bg-[#F7F4EE] hover:text-[#26312C]"
              >
                <LockKeyhole className="h-3.5 w-3.5" />
                锁定
              </button>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1F4E43] text-[11px] font-bold text-white">
                管
              </span>
            </div>
          </header>

          <main className="mx-auto w-full max-w-[1240px] px-4 py-6 sm:px-6 lg:px-8 lg:py-7">
            <Outlet />
          </main>
        </div>
      </div>
    </AdminAuthContext.Provider>
  )
}