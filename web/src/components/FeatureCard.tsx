import type { LucideIcon } from 'lucide-react'
import { ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { toneStyles, type Tone } from './Tag'

interface FeatureCardProps {
  to: string
  title: string
  description: string
  icon: LucideIcon
  accent?: Tone
  meta?: string
}

const borderMap: Record<Tone, string> = {
  blue: 'border-l-blue-500',
  emerald: 'border-l-emerald-500',
  cyan: 'border-l-cyan-500',
  amber: 'border-l-amber-500',
  violet: 'border-l-violet-500',
  red: 'border-l-red-500',
  slate: 'border-l-slate-400',
}

export function FeatureCard({
  to,
  title,
  description,
  icon: Icon,
  accent = 'blue',
  meta,
}: FeatureCardProps) {
  const styles = toneStyles[accent]
  return (
    <Link
      to={to}
      className={`group relative flex items-start gap-4 overflow-hidden rounded-xl border border-slate-200 border-l-4 ${borderMap[accent]} bg-white p-5 shadow-sm shadow-slate-900/[0.02] transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md`}
    >
      <span
        className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${styles.soft}`}
      >
        <Icon className={`h-5 w-5 ${styles.icon}`} strokeWidth={1.8} />
      </span>
      <span className="min-w-0 flex-1">
        <span className="flex items-center justify-between gap-2">
          <span className="text-sm font-semibold text-slate-900">{title}</span>
          <ArrowUpRight className="h-4 w-4 shrink-0 text-slate-300 transition-colors group-hover:text-slate-500" />
        </span>
        <span className="mt-1.5 block text-xs leading-relaxed text-slate-500">
          {description}
        </span>
        {meta ? (
          <span className="mt-3 block text-[11px] font-medium text-slate-400">
            {meta}
          </span>
        ) : null}
      </span>
    </Link>
  )
}
