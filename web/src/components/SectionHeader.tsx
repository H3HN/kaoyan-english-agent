import type { ReactNode } from 'react'

interface SectionHeaderProps {
  title: string
  description?: string
  action?: ReactNode
}

export function SectionHeader({
  title,
  description,
  action,
}: SectionHeaderProps) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        <h2 className="text-[17px] font-semibold tracking-tight text-slate-900">
          {title}
        </h2>
        {description ? (
          <p className="mt-1 text-xs leading-relaxed text-slate-500">
            {description}
          </p>
        ) : null}
      </div>
      {action}
    </div>
  )
}
