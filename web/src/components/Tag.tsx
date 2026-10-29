import type { ReactNode } from 'react'

export type Tone =
  | 'blue'
  | 'emerald'
  | 'cyan'
  | 'amber'
  | 'violet'
  | 'red'
  | 'slate'

export const toneStyles: Record<
  Tone,
  { bar: string; soft: string; text: string; icon: string; dot: string }
> = {
  blue: {
    bar: 'bg-blue-500',
    soft: 'bg-blue-50',
    text: 'text-blue-700',
    icon: 'text-blue-600',
    dot: 'bg-blue-500',
  },
  emerald: {
    bar: 'bg-emerald-500',
    soft: 'bg-emerald-50',
    text: 'text-emerald-700',
    icon: 'text-emerald-600',
    dot: 'bg-emerald-500',
  },
  cyan: {
    bar: 'bg-cyan-500',
    soft: 'bg-cyan-50',
    text: 'text-cyan-700',
    icon: 'text-cyan-600',
    dot: 'bg-cyan-500',
  },
  amber: {
    bar: 'bg-amber-500',
    soft: 'bg-amber-50',
    text: 'text-amber-700',
    icon: 'text-amber-600',
    dot: 'bg-amber-500',
  },
  violet: {
    bar: 'bg-violet-500',
    soft: 'bg-violet-50',
    text: 'text-violet-700',
    icon: 'text-violet-600',
    dot: 'bg-violet-500',
  },
  red: {
    bar: 'bg-red-500',
    soft: 'bg-red-50',
    text: 'text-red-700',
    icon: 'text-red-600',
    dot: 'bg-red-500',
  },
  slate: {
    bar: 'bg-slate-400',
    soft: 'bg-slate-100',
    text: 'text-slate-600',
    icon: 'text-slate-500',
    dot: 'bg-slate-400',
  },
}

interface TagProps {
  tone?: Tone
  children: ReactNode
  dot?: boolean
  pill?: boolean
  className?: string
  title?: string
}

export function Tag({
  tone = 'slate',
  children,
  dot = false,
  pill = false,
  className = '',
  title,
}: TagProps) {
  const styles = toneStyles[tone]
  return (
    <span
      title={title}
      className={`inline-flex items-center gap-1.5 rounded-lg px-2 py-0.5 text-[11px] font-medium ${styles.soft} ${styles.text} ${pill ? 'rounded-full' : ''} ${className}`}
    >
      {dot ? <span className={`h-1.5 w-1.5 rounded-full ${styles.dot}`} /> : null}
      {children}
    </span>
  )
}
