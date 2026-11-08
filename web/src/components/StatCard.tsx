import type { LucideIcon } from 'lucide-react'
import { Link } from 'react-router-dom'
import { toneStyles, type Tone } from './Tag'

interface StatCardProps {
  label: string
  value: string | number
  hint?: string
  icon?: LucideIcon
  accent?: Tone
  to?: string
  loading?: boolean
}

export function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  accent = 'blue',
  to,
  loading = false,
}: StatCardProps) {
  const styles = toneStyles[accent]
  const body = (
    <>
      <span className={`absolute inset-x-0 top-0 h-1 ${styles.bar}`} />
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-xs font-medium text-slate-500">{label}</p>
          {loading ? (
            <span className="mt-3 block h-8 w-24 animate-pulse rounded-md bg-slate-100" />
          ) : (
            <p className="mt-2 text-3xl font-bold tracking-tight text-slate-900 tabular-nums">
              {value}
            </p>
          )}
        </div>
        {Icon ? (
          <span
            className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg ${styles.soft}`}
          >
            <Icon className={`h-[18px] w-[18px] ${styles.icon}`} strokeWidth={1.8} />
          </span>
        ) : null}
      </div>
      <div className="mt-3 min-h-[2.1rem]">
        {loading ? (
          <span className="block h-3 w-40 animate-pulse rounded bg-slate-100" />
        ) : hint ? (
          <p className="text-[11px] leading-relaxed text-slate-400">{hint}</p>
        ) : null}
      </div>
    </>
  )

  const base =
    'relative overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-900/[0.02]'

  if (to) {
    return (
      <Link
        to={to}
        className={`${base} block transition-all hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md hover:shadow-slate-900/[0.06]`}
      >
        {body}
      </Link>
    )
  }

  return <div className={base}>{body}</div>
}
