import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: ReactNode
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 bg-white px-6 py-14 text-center">
      {Icon ? (
        <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-slate-50">
          <Icon className="h-5 w-5 text-slate-400" strokeWidth={1.8} />
        </span>
      ) : null}
      <p className="mt-4 text-sm font-semibold text-slate-800">{title}</p>
      {description ? (
        <p className="mt-1.5 max-w-md text-xs leading-relaxed text-slate-500">
          {description}
        </p>
      ) : null}
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  )
}
