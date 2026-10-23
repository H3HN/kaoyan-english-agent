import type { ReactNode } from 'react'

interface PageHeroProps {
  eyebrow?: string
  title: string
  subtitle: string
  actions?: ReactNode
}

export function PageHero({
  eyebrow = 'KAOYAN ENGLISH STUDIO',
  title,
  subtitle,
  actions,
}: PageHeroProps) {
  return (
    <section className="relative overflow-hidden rounded-2xl bg-slate-800 px-6 py-7 text-white shadow-sm sm:px-8 sm:py-8">
      <div className="pointer-events-none absolute -right-20 -top-28 h-64 w-64 rounded-full bg-blue-500/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-24 right-24 h-48 w-48 rounded-full bg-cyan-400/5 blur-3xl" />
      <div className="relative flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
        <div className="min-w-0">
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
            {eyebrow}
          </p>
          <h1 className="mt-2 text-balance text-2xl font-bold tracking-tight text-white sm:text-[28px]">
            {title}
          </h1>
          <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-300">
            {subtitle}
          </p>
        </div>
        {actions ? (
          <div className="flex shrink-0 flex-wrap items-center gap-2">
            {actions}
          </div>
        ) : null}
      </div>
    </section>
  )
}
