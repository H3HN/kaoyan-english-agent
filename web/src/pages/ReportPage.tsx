import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  BookMarked,
  CalendarDays,
  CheckCircle2,
  ChevronRight,
  Lightbulb,
  Target,
  TrendingUp,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { PageHero } from '../components/PageHero'
import { ProgressBar } from '../components/ProgressBar'
import { SectionHeader } from '../components/SectionHeader'
import { StatCard } from '../components/StatCard'
import { Tag } from '../components/Tag'
import { QUESTION_TYPES } from '../data/content'
import { formatRelative } from '../lib/format'
import { useAppStore } from '../store/AppStore'

export default function ReportPage() {
  const { records, dueWords } = useAppStore()
  const total = records.length
  const correct = records.filter((record) => record.isCorrect).length
  const accuracy = total > 0 ? correct / total : 0

  const byType = QUESTION_TYPES.map((type) => {
    const items = records.filter((record) => record.questionType === type.name)
    const typeCorrect = items.filter((record) => record.isCorrect).length
    return {
      ...type,
      total: items.length,
      correct: typeCorrect,
      accuracy: items.length > 0 ? typeCorrect / items.length : 0,
    }
  })

  const weakTypes = byType
    .filter((item) => item.total > 0 && item.accuracy < 0.7)
    .sort((a, b) => a.accuracy - b.accuracy)

  const days = Array.from({ length: 7 }, (_, index) => {
    const date = new Date()
    date.setDate(date.getDate() - (6 - index))
    const count = records.filter((record) => {
      const time = new Date(record.time)
      return (
        time.getFullYear() === date.getFullYear() &&
        time.getMonth() === date.getMonth() &&
        time.getDate() === date.getDate()
      )
    }).length
    return {
      key: date.toISOString(),
      label: new Intl.DateTimeFormat('zh-CN', { weekday: 'short' }).format(
        date,
      ),
      count,
    }
  })
  const maxCount = Math.max(1, ...days.map((day) => day.count))

  const suggestions: string[] = []
  if (weakTypes.length > 0) {
    weakTypes.slice(0, 2).forEach((item) => {
      suggestions.push(
        `${item.name}正确率 ${Math.round(item.accuracy * 100)}%，建议从真题中筛出同类题，每天精做 2–3 道并复述排除理由。`,
      )
    })
  } else {
    suggestions.push('各题型正确率均达标，保持当前节奏，尝试限时训练提升速度。')
  }
  if (dueWords.length > 0) {
    suggestions.push(
      `今天有 ${dueWords.length} 个单词到期，先完成一轮无提示回忆，再开始新的阅读。`,
    )
  }
  if (total < 30) {
    suggestions.push(
      `目前累计 ${total} 题，样本还不够大。建议先累计 30 题以上，再做稳定的薄弱分析。`,
    )
  }
  suggestions.push(
    '每完成一题，固定写下一句“为什么排除”，比只记正确答案更有迁移价值。',
  )

  return (
    <div className="space-y-6">
      <PageHero
        eyebrow="LEARNING ANALYTICS"
        title="学习报告"
        subtitle="不只看正确率，也看错误集中在哪。把每一次答题记录变成下一轮训练的输入。"
        actions={
          <Link
            to="/options"
            className="inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 transition-colors hover:bg-slate-100"
          >
            继续练习
            <ArrowRight className="h-4 w-4" />
          </Link>
        }
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="总练习题数"
          value={total}
          hint="来自选项分析与真题练习"
          icon={Target}
          accent="blue"
        />
        <StatCard
          label="正确题数"
          value={correct}
          hint="已记录为正确的答案"
          icon={CheckCircle2}
          accent="emerald"
        />
        <StatCard
          label="整体正确率"
          value={`${Math.round(accuracy * 100)}%`}
          hint={total > 0 ? `${correct} / ${total}` : '暂无记录'}
          icon={TrendingUp}
          accent="violet"
        />
        <StatCard
          label="待复习单词"
          value={dueWords.length}
          hint="到期单词优先处理"
          icon={BookMarked}
          accent="amber"
        />
      </div>

      {total > 0 ? (
        <>
          <div className="grid gap-6 lg:grid-cols-3">
            <section className="lg:col-span-2">
              <SectionHeader
                title="各题型正确率"
                description="正确率低于 70% 的题型会在右侧标为薄弱项。"
                action={
                  <span className="inline-flex items-center gap-1.5 text-[11px] text-slate-400">
                    <BarChart3 className="h-3.5 w-3.5" />
                    {byType.filter((item) => item.total > 0).length} 类已练习
                  </span>
                }
              />
              <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
                <div className="space-y-5">
                  {byType.map((item) => {
                    const percent = Math.round(item.accuracy * 100)
                    const tone =
                      item.total === 0
                        ? 'slate'
                        : item.accuracy >= 0.8
                          ? 'emerald'
                          : item.accuracy >= 0.7
                            ? 'blue'
                            : item.accuracy >= 0.5
                              ? 'amber'
                              : 'red'
                    return (
                      <div key={item.name}>
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="text-xs font-semibold text-slate-800">
                              {item.name}
                            </span>
                            <span className="text-[10px] text-slate-400">
                              {item.correct} / {item.total} 题
                            </span>
                            {item.total > 0 && item.accuracy < 0.7 ? (
                              <Tag tone="red">薄弱</Tag>
                            ) : null}
                          </div>
                          <span className="text-[11px] font-semibold text-slate-600 tabular-nums">
                            {item.total > 0 ? `${percent}%` : '—'}
                          </span>
                        </div>
                        <ProgressBar
                          value={item.total > 0 ? percent : 0}
                          tone={tone}
                          className="mt-2"
                        />
                      </div>
                    )
                  })}
                </div>
              </div>
            </section>

            <section>
              <SectionHeader
                title="薄弱环节"
                description="按正确率从低到高排序。"
              />
              <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                {weakTypes.length > 0 ? (
                  <div className="space-y-3">
                    {weakTypes.map((item) => (
                      <div
                        key={item.name}
                        className="rounded-lg border border-red-100 bg-red-50/60 px-3.5 py-3"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="h-3.5 w-3.5 text-red-500" />
                            <span className="text-xs font-semibold text-slate-800">
                              {item.name}
                            </span>
                          </div>
                          <Tag tone="red">
                            {Math.round(item.accuracy * 100)}%
                          </Tag>
                        </div>
                        <p className="mt-1.5 text-[11px] leading-relaxed text-slate-500">
                          {item.steps[0]}；优先用同类真题做针对性训练。
                        </p>
                      </div>
                    ))}
                    <Link
                      to="/options"
                      className="flex items-center justify-between rounded-lg border border-slate-200 px-3.5 py-2.5 text-[11px] font-medium text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-800"
                    >
                      去练一道薄弱题型
                      <ChevronRight className="h-3.5 w-3.5" />
                    </Link>
                  </div>
                ) : (
                  <div className="flex flex-col items-center py-6 text-center">
                    <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50">
                      <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                    </span>
                    <p className="mt-3 text-xs font-semibold text-slate-800">
                      各题型均达标
                    </p>
                    <p className="mt-1 text-[11px] leading-relaxed text-slate-400">
                      正确率都在 70% 以上，继续保持。
                    </p>
                  </div>
                )}
              </div>
            </section>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <section>
              <SectionHeader
                title="备考建议"
                description="根据当前记录自动生成，不是通用鸡汤。"
              />
              <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
                <div className="space-y-3.5">
                  {suggestions.map((suggestion, index) => (
                    <div key={suggestion} className="flex items-start gap-3">
                      <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-slate-50 text-[10px] font-bold text-slate-500 ring-1 ring-slate-100">
                        {index + 1}
                      </span>
                      <p className="text-xs leading-relaxed text-slate-600">
                        {suggestion}
                      </p>
                    </div>
                  ))}
                </div>
                <div className="mt-5 flex items-start gap-2 rounded-lg bg-blue-50/70 px-3.5 py-3">
                  <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0 text-blue-500" />
                  <p className="text-[11px] leading-relaxed text-blue-900/70">
                    建议每次只改一个变量：要么限时，要么专项，要么复盘。不要同时追求所有指标。
                  </p>
                </div>
              </div>
            </section>

            <section>
              <SectionHeader
                title="近 7 天练习量"
                description="用练习频次检查节奏，而不是只盯正确率。"
                action={
                  <span className="inline-flex items-center gap-1.5 text-[11px] text-slate-400">
                    <CalendarDays className="h-3.5 w-3.5" />
                    最近一周
                  </span>
                }
              />
              <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
                <div className="flex h-36 items-end gap-3">
                  {days.map((day) => {
                    const height =
                      day.count > 0
                        ? Math.max(10, (day.count / maxCount) * 100)
                        : 4
                    return (
                      <div
                        key={day.key}
                        className="flex h-full flex-1 flex-col items-center justify-end gap-2"
                      >
                        <span className="text-[10px] font-medium text-slate-400">
                          {day.count > 0 ? day.count : ''}
                        </span>
                        <div className="flex w-full flex-1 items-end">
                          <div
                            className={`w-full rounded-t-md transition-all ${
                              day.count > 0 ? 'bg-slate-700' : 'bg-slate-100'
                            }`}
                            style={{ height: `${height}%` }}
                          />
                        </div>
                        <span className="text-[10px] text-slate-400">
                          {day.label}
                        </span>
                      </div>
                    )
                  })}
                </div>
                <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3 text-[11px] text-slate-400">
                  <span>本周合计</span>
                  <span className="font-semibold text-slate-700">
                    {days.reduce((sum, day) => sum + day.count, 0)} 题
                  </span>
                </div>
              </div>
            </section>
          </div>

          <section>
            <SectionHeader
              title="最近练习"
              description="按时间倒序，保留每次选择的答案。"
            />
            <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="hidden grid-cols-[1fr_150px_90px_100px] border-b border-slate-100 bg-slate-50/70 px-5 py-3 text-[11px] font-medium text-slate-400 sm:grid">
                <span>题型</span>
                <span>作答</span>
                <span>结果</span>
                <span className="text-right">时间</span>
              </div>
              {records.slice(0, 8).map((record) => (
                <div
                  key={record.id}
                  className="flex items-center justify-between gap-3 border-b border-slate-100 px-5 py-3.5 last:border-b-0 sm:grid sm:grid-cols-[1fr_150px_90px_100px]"
                >
                  <Tag tone="violet">{record.questionType}</Tag>
                  <span className="hidden text-xs text-slate-500 sm:block">
                    选 {record.userAnswer} · 答案 {record.correctAnswer}
                  </span>
                  <div>
                    <Tag tone={record.isCorrect ? 'emerald' : 'red'} dot>
                      {record.isCorrect ? '正确' : '错误'}
                    </Tag>
                  </div>
                  <span className="text-right text-[11px] text-slate-400">
                    {formatRelative(record.time)}
                  </span>
                </div>
              ))}
            </div>
          </section>
        </>
      ) : (
        <EmptyState
          icon={BarChart3}
          title="还没有足够的学习记录"
          description="完成一题后，这里会自动生成正确率、薄弱环节与备考建议。"
          action={
            <Link
              to="/options"
              className="inline-flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2.5 text-xs font-semibold text-white hover:bg-slate-900"
            >
              去做第一题
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          }
        />
      )}
    </div>
  )
}
