import { useEffect, useState, type FormEvent } from 'react'
import {
  ArrowRight,
  CalendarDays,
  CalendarCheck,
  CheckCircle2,
  ChevronRight,
  Circle,
  Clock,
  Loader2,
  RefreshCw,
  Target,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { EmptyState } from '../components/EmptyState'
import { PageHero } from '../components/PageHero'
import { ProgressBar } from '../components/ProgressBar'
import { SectionHeader } from '../components/SectionHeader'
import { StatCard } from '../components/StatCard'
import { Tag } from '../components/Tag'
import {
  api,
  type PlanItem,
  type PlanResponse,
  type PlanSettings,
} from '../lib/api'

export default function PlanPage() {
  const [plan, setPlan] = useState<PlanResponse | null>(null)
  const [settings, setSettings] = useState<PlanSettings | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [busyId, setBusyId] = useState<number | null>(null)
  const [regenerating, setRegenerating] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const load = () => {
    setLoading(true)
    Promise.all([api.getPlan(0), api.getPlanSettings()])
      .then(([planData, settingsData]) => {
        setPlan(planData)
        setSettings(settingsData)
        setError(false)
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  // First visit: every rule-based task needs a plan row, so create one once.
  useEffect(() => {
    if (!loading && plan && plan.summary.total === 0) {
      api
        .generatePlan()
        .then((data) => setPlan(data))
        .catch(() => setError(true))
    }
  }, [loading, plan])

  const toggleItem = async (item: PlanItem) => {
    const nextDone = item.status !== 'done'
    setBusyId(item.id)
    try {
      await api.completePlanItem(item.id, nextDone)
      setPlan(await api.getPlan(0))
    } catch {
      setError(true)
    } finally {
      setBusyId(null)
    }
  }

  const regenerate = async () => {
    setRegenerating(true)
    try {
      const data = await api.generatePlan(true)
      setPlan(data)
      setError(false)
    } catch {
      setError(true)
    } finally {
      setRegenerating(false)
    }
  }

  const saveSettings = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!settings) return
    setSaving(true)
    try {
      setSettings(
        await api.updatePlanSettings({
          exam_date: settings.exam_date,
          daily_minutes: settings.daily_minutes,
          target_score: settings.target_score,
        }),
      )
      setSaved(true)
      window.setTimeout(() => setSaved(false), 2000)
    } catch {
      setError(true)
    } finally {
      setSaving(false)
    }
  }

  if (loading && !plan) {
    return (
      <div
        role="status"
        className="flex items-center justify-center rounded-xl border border-slate-200 bg-white p-8 text-sm text-slate-500"
      >
        正在加载学习计划…
      </div>
    )
  }

  if (error && !plan) {
    return (
      <EmptyState
        icon={CalendarCheck}
        title="暂时无法读取学习计划"
        action={
          <button
            type="button"
            onClick={load}
            className="inline-flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2.5 text-xs font-semibold text-white hover:bg-slate-900"
          >
            重试
            <RefreshCw className="h-3.5 w-3.5" />
          </button>
        }
      />
    )
  }

  const summary = plan?.summary ?? { total: 0, done: 0, pending: 0, ratio: 0 }
  const days = plan?.days ?? []
  const examDate = settings?.exam_date ?? ''
  const countdown = examDate
    ? Math.ceil(
        (new Date(`${examDate}T00:00:00`).getTime() - Date.now()) / 86400000,
      )
    : null

  return (
    <div className="space-y-6">
      <PageHero
        eyebrow="STUDY SCHEDULER"
        title="学习计划"
        actions={
          <button
            type="button"
            onClick={regenerate}
            disabled={regenerating}
            className="inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 transition-colors hover:bg-slate-100 disabled:opacity-60"
          >
            <RefreshCw
              className={`h-4 w-4 ${regenerating ? 'animate-spin' : ''}`}
            />
            {regenerating ? '正在重排…' : '重新生成'}
          </button>
        }
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="本周任务"
          value={summary.total}
          icon={CalendarDays}
          accent="blue"
        />
        <StatCard
          label="已完成"
          value={summary.done}
          hint={`还有 ${summary.pending} 项待完成`}
          icon={CheckCircle2}
          accent="emerald"
        />
        <StatCard
          label="完成率"
          value={`${Math.round(summary.ratio * 100)}%`}
          icon={Target}
          accent="violet"
        />
        <StatCard
          label="距考试"
          value={countdown === null ? '未设置' : countdown > 0 ? `${countdown} 天` : '已到考试日'}
          hint={examDate || '在下方设置考试日期'}
          icon={Clock}
          accent="amber"
        />
      </div>

      <section>
        <SectionHeader title="排程偏好" />
        <form
          onSubmit={saveSettings}
          className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6"
        >
          <div className="grid gap-4 sm:grid-cols-3">
            <label className="block">
              <span className="text-[11px] font-medium text-slate-500">
                考试日期
              </span>
              <input
                type="date"
                value={settings?.exam_date ?? ''}
                onChange={(event) =>
                  setSettings((prev) =>
                    prev ? { ...prev, exam_date: event.target.value } : prev,
                  )
                }
                className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2 text-xs text-slate-700 outline-none focus:border-slate-400"
              />
            </label>
            <label className="block">
              <span className="text-[11px] font-medium text-slate-500">
                每日可用时间（分钟）
              </span>
              <input
                type="number"
                min={10}
                max={480}
                step={5}
                value={settings?.daily_minutes ?? 60}
                onChange={(event) =>
                  setSettings((prev) =>
                    prev
                      ? { ...prev, daily_minutes: Number(event.target.value) }
                      : prev,
                  )
                }
                className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2 text-xs text-slate-700 outline-none focus:border-slate-400"
              />
            </label>
            <label className="block">
              <span className="text-[11px] font-medium text-slate-500">
                目标分数
              </span>
              <input
                type="number"
                min={0}
                max={100}
                step={5}
                value={settings?.target_score ?? 70}
                onChange={(event) =>
                  setSettings((prev) =>
                    prev
                      ? { ...prev, target_score: Number(event.target.value) }
                      : prev,
                  )
                }
                className="mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2 text-xs text-slate-700 outline-none focus:border-slate-400"
              />
            </label>
          </div>
          <div className="mt-4 flex items-center justify-between gap-3">
            <p className="text-[11px] leading-relaxed text-slate-400">
              排程完全由规则引擎计算：到期单词、薄弱题型、未做真题决定每天做什么，结果可追溯到数据库状态。
            </p>
            <button
              type="submit"
              disabled={saving}
              className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-slate-800 px-3.5 py-2 text-xs font-semibold text-white transition-colors hover:bg-slate-900 disabled:opacity-60"
            >
              {saving ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : null}
              {saved ? '已保存' : '保存偏好'}
            </button>
          </div>
        </form>
      </section>

      <section>
        <SectionHeader
          title="未来 7 天"
          action={
            <Link
              to="/report"
              className="inline-flex items-center gap-1 text-xs font-medium text-slate-500 transition-colors hover:text-slate-800"
            >
              查看学习报告
              <ChevronRight className="h-3.5 w-3.5" />
            </Link>
          }
        />
        <div className="space-y-3">
          {days.map((day) => (
            <div
              key={day.date}
              className={`overflow-hidden rounded-xl border bg-white shadow-sm ${
                day.is_today ? 'border-slate-300' : 'border-slate-200'
              }`}
            >
              <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50/60 px-5 py-2.5">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-semibold ${
                      day.is_today ? 'text-slate-900' : 'text-slate-600'
                    }`}
                  >
                    {day.date.slice(5)} · {day.weekday}
                  </span>
                  {day.is_today ? <Tag tone="blue">今天</Tag> : null}
                </div>
                <span className="text-[11px] text-slate-400">
                  {day.done_count} / {day.total_count}
                </span>
              </div>
              {day.items.length > 0 ? (
                day.items.map((item) => {
                  const done = item.status === 'done'
                  return (
                    <div
                      key={item.id}
                      className="flex items-center gap-3 border-b border-slate-100 px-5 py-3 last:border-b-0"
                    >
                      <button
                        type="button"
                        role="checkbox"
                        aria-checked={done}
                        aria-label={`${done ? '取消完成' : '标记完成'}：${item.title}`}
                        disabled={busyId === item.id}
                        onClick={() => void toggleItem(item)}
                        className="shrink-0 text-slate-400 transition-colors hover:text-emerald-600 disabled:opacity-50"
                      >
                        {done ? (
                          <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                        ) : (
                          <Circle className="h-5 w-5" />
                        )}
                      </button>
                      <div className="min-w-0 flex-1">
                        <p
                          className={`text-xs font-semibold ${
                            done
                              ? 'text-slate-400 line-through'
                              : 'text-slate-800'
                          }`}
                        >
                          {item.title}
                        </p>
                        <p className="mt-0.5 text-[10px] text-slate-400">
                          {item.task_type === 'vocab_review'
                            ? '单词复习'
                            : item.task_type === 'weak_type_practice'
                              ? '薄弱题型专项'
                              : item.task_type === 'exam_practice'
                                ? '真题训练'
                                : '长难句练习'}
                          {item.target_count > 1
                            ? ` · 目标 ${item.target_count} 项`
                            : ''}
                        </p>
                      </div>
                      <Link
                        to={item.link || '/options'}
                        className="inline-flex shrink-0 items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1.5 text-[10px] font-medium text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-800"
                      >
                        去完成
                        <ArrowRight className="h-3 w-3" />
                      </Link>
                    </div>
                  )
                })
              ) : (
                <p className="px-5 py-4 text-[11px] text-slate-400">
                  当天暂无任务，可点击右上角「重新生成」按最新数据补排。
                </p>
              )}
            </div>
          ))}
        </div>
      </section>

      {summary.total > 0 ? (
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="flex items-center justify-between gap-3">
            <span className="text-xs font-semibold text-slate-700">
              本周完成进度
            </span>
            <span className="text-[11px] font-semibold text-slate-600 tabular-nums">
              {summary.done} / {summary.total}
            </span>
          </div>
          <ProgressBar
            value={Math.round(summary.ratio * 100)}
            tone={summary.ratio >= 0.8 ? 'emerald' : 'blue'}
            className="mt-3"
          />
        </section>
      ) : null}
    </div>
  )
}