import type { ReactNode } from 'react'
import { CheckCircle2, XCircle } from 'lucide-react'

interface ComparePanelProps {
  left: ReactNode
  right: ReactNode
  leftTitle?: string
  rightTitle?: string
  className?: string
}

export function ComparePanel({
  left,
  right,
  leftTitle = '通用模型',
  rightTitle = '定制 Agent',
  className = '',
}: ComparePanelProps) {
  return (
    <div
      className={`overflow-hidden rounded-xl border border-slate-200 bg-white ${className}`}
    >
      <div className="grid md:grid-cols-2">
        <div className="flex flex-col border-b border-slate-200 md:border-b-0 md:border-r">
          <div className="flex items-center gap-2 border-b border-red-100 bg-red-50 px-5 py-3">
            <XCircle className="h-4 w-4 text-red-500" strokeWidth={1.8} />
            <span className="text-xs font-semibold text-red-700">
              {leftTitle}
            </span>
          </div>
          <div className="flex-1 px-5 py-5 text-sm leading-relaxed text-slate-600">
            {left}
          </div>
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2 border-b border-emerald-100 bg-emerald-50 px-5 py-3">
            <CheckCircle2
              className="h-4 w-4 text-emerald-500"
              strokeWidth={1.8}
            />
            <span className="text-xs font-semibold text-emerald-700">
              {rightTitle}
            </span>
          </div>
          <div className="flex-1 px-5 py-5 text-sm leading-relaxed text-slate-600">
            {right}
          </div>
        </div>
      </div>
    </div>
  )
}
