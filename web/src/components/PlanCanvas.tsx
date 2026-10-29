import { useState } from 'react'
import { CalendarDays, CheckCircle2, ChevronRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { api, type ScheduleTask } from '../lib/api'
import { Tag } from './Tag'

export function PlanCanvas({
  data,
}: {
  data: { source_label?: string; tasks: ScheduleTask[] }
}) {
  const [tasks, setTasks] = useState(data.tasks ?? [])

  const complete = async (task: ScheduleTask) => {
    const completed = task.status !== 'completed'
    setTasks((prev) =>
      prev.map((item) =>
        item.id === task.id
          ? { ...item, status: completed ? 'completed' : 'pending' }
          : item,
      ),
    )
    try {
      await api.completeScheduleTask(task.id, completed)
    } catch {
      setTasks((prev) =>
        prev.map((item) =>
          item.id === task.id ? { ...item, status: task.status } : item,
        ),
      )
    }
  }

  return (
    <div className="space-y-3">
      <section className="rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-sm">
        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
          LEARNING PLAN · 可执行计划
        </p>
        <h1 className="mt-1 text-xl font-bold tracking-tight">按错题生成的学习计划</h1>
        <p className="mt-1 text-[11px] text-slate-300">
          {data.source_label ?? '根据最近薄弱项与到期词生成'} · {tasks.length} 项任务
        </p>
      </section>

      <div className="grid gap-3 lg:grid-cols-3">
        {tasks.map((task) => (
          <section
            key={task.id}
            className={`flex min-h-[190px] flex-col rounded-2xl border bg-white p-4 shadow-sm ${
              task.status === 'completed' ? 'border-emerald-200' : 'border-slate-200'
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <Tag tone={task.status === 'completed' ? 'emerald' : 'violet'}>
                {task.day_label}
              </Tag>
              <span className="text-[9px] text-slate-400">{task.task_type}</span>
            </div>
            <p className={`mt-3 text-sm font-semibold leading-6 ${
              task.status === 'completed' ? 'text-slate-400 line-through' : 'text-slate-800'
            }`}>
              {task.title}
            </p>
            <p className="mt-1 text-[11px] leading-5 text-slate-400">{task.agent_reason}</p>
            <div className="mt-auto flex items-center justify-between gap-2 pt-4">
              <button
                type="button"
                onClick={() => void complete(task)}
                className={`inline-flex items-center gap-1 text-[10px] font-medium ${
                  task.status === 'completed' ? 'text-emerald-600' : 'text-slate-500 hover:text-slate-800'
                }`}
              >
                <CheckCircle2 className="h-3 w-3" />
                {task.status === 'completed' ? '已完成' : '标记完成'}
              </button>
              <Link
                to={task.target_route || '/studio'}
                className="inline-flex items-center gap-1 text-[10px] font-medium text-blue-600 hover:text-blue-800"
              >
                执行 <ChevronRight className="h-3 w-3" />
              </Link>
            </div>
          </section>
        ))}
      </div>

      {!tasks.length ? (
        <div className="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center text-sm text-slate-400">
          没有生成计划，请让 Agent 根据最近错题重新安排。
        </div>
      ) : (
        <div className="flex items-center gap-1.5 px-1 text-[10px] text-slate-400">
          <CalendarDays className="h-3 w-3" />
          计划已写入 study_schedule_tasks，勾选会实时写回 SQLite。
        </div>
      )}
    </div>
  )
}
