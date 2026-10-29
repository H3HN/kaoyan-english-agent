import { AlertTriangle, ListChecks, ShieldCheck } from 'lucide-react'
import type { TrapMethodCard } from '../lib/api'
import { Tag } from './Tag'

export function TrapMethodCardView({
  card,
  hitCount,
}: {
  card: TrapMethodCard
  hitCount?: number
}) {
  return (
    <section className="mt-4 rounded-xl border border-slate-200 border-l-4 border-l-red-400 bg-white p-4">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
            <AlertTriangle className="h-4 w-4 text-red-500" />
            陷阱方法卡 · {card.name}
          </p>
          <p className="mt-1 text-xs leading-5 text-slate-500">{card.definition}</p>
        </div>
        {typeof hitCount === 'number' && hitCount > 0 ? (
          <Tag tone="red">历史命中 {hitCount} 次</Tag>
        ) : null}
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">
            识别信号
          </p>
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {card.signals.map((signal) => (
              <span key={signal} className="rounded-md bg-slate-50 px-2 py-1 text-[10px] text-slate-600 ring-1 ring-slate-100">
                {signal}
              </span>
            ))}
          </div>
        </div>
        <div>
          <p className="flex items-center gap-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">
            <ListChecks className="h-3 w-3" /> 排除步骤
          </p>
          <ol className="mt-1.5 space-y-1">
            {card.steps.map((step, index) => (
              <li key={step} className="flex gap-1.5 text-[10px] leading-5 text-slate-600">
                <span className="font-semibold text-slate-400">{index + 1}.</span>
                {step}
              </li>
            ))}
          </ol>
        </div>
      </div>

      <div className="mt-3 flex items-start gap-2 rounded-lg bg-emerald-50 px-3 py-2">
        <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-600" />
        <p className="text-[11px] leading-5 text-emerald-800">
          <span className="font-semibold">正确项长什么样：</span>
          {card.correct_pattern}
        </p>
      </div>
    </section>
  )
}
