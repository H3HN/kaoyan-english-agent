import type { Tone } from './Tag'
import { toneStyles } from './Tag'

interface ProgressBarProps {
  value: number
  tone?: Tone
  className?: string
}

export function ProgressBar({
  value,
  tone = 'blue',
  className = '',
}: ProgressBarProps) {
  const styles = toneStyles[tone]
  const clamped = Math.max(0, Math.min(100, value))
  return (
    <div
      className={`h-1.5 w-full overflow-hidden rounded-full bg-slate-100 ${className}`}
      role="progressbar"
      aria-valuenow={Math.round(clamped)}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className={`h-full rounded-full transition-all duration-300 ${styles.bar}`}
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
