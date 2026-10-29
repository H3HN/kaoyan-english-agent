import { useEffect, useState } from 'react'
import { ArrowRight, BookOpen, Brain, CalendarDays, ClipboardPaste, Headphones, Layers3, PenLine, Sparkles } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { api, type LearnerGoal, type LearnerProfile, type ScheduleTask } from '../lib/api'
import { useAppStore } from '../store/AppStore'
import { useSession } from '../store/SessionStore'
import { useUI } from '../store/UIStore'
import { useWorkspace } from '../store/WorkspaceStore'
import { OmniComposer } from './OmniComposer'

export function ZeroState() {
  const { dueWords } = useAppStore()
  const { messages, sendMessage } = useSession()
  const { setFlashcardOpen, setDraft } = useUI()
  const { openWorkspaceUnit } = useWorkspace()
  const navigate = useNavigate()
  const [tasks, setTasks] = useState<ScheduleTask[]>([])
  const [profile, setProfile] = useState<LearnerProfile | null>(null)
  const [goal, setGoal] = useState<LearnerGoal | null>(null)
  const [goalSaving, setGoalSaving] = useState(false)
  const [goalForm, setGoalForm] = useState({ target_score: 70, exam_date: '', daily_minutes: 30, current_level: '基础' })

  useEffect(() => {
    let alive = true
    api
      .getSchedule()
      .then((response) => {
        if (alive) setTasks(response.items)
      })
      .catch(() => {})
    api
      .getLearnerProfile()
      .then((response) => {
        if (alive) setProfile(response)
      })
      .catch(() => {})
    api
      .getLearnerGoal()
      .then((response) => {
        if (!alive) return
        setGoal(response.goal)
        if (response.goal) {
          setGoalForm({
            target_score: response.goal.target_score,
            exam_date: response.goal.exam_date,
            daily_minutes: response.goal.daily_minutes,
            current_level: response.goal.current_level,
          })
        }
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [])

  const urgent = tasks.find((task) => task.status === 'pending')
  const weakestTrap = profile?.weakest_trap ?? '阅读细节题'
  const nextAction = dueWords.length
    ? {
        label: `先复习 ${dueWords.length} 个到期词`,
        hint: `来自今日 SRS 队列 · 最弱陷阱：${weakestTrap}${goal ? ` · 今日 ${goal.daily_minutes} 分钟` : ''}`,
        action: () => setFlashcardOpen(true),
      }
    : urgent
      ? {
          label: urgent.title,
          hint: `${urgent.agent_reason} · 刚刚生成的学习任务`,
          action: () => {
            if (urgent.task_type === 'READING') {
              void sendMessage('今天读什么？请直接给我文章并带我去。')
            } else if (urgent.task_type === 'VOCAB') {
              setFlashcardOpen(true)
            } else {
              navigate(urgent.target_route || '/studio')
            }
          },
        }
      : {
          label: '先读一篇真题阅读',
          hint: `当前最弱陷阱：${weakestTrap}${goal ? ` · 今日 ${goal.daily_minutes} 分钟` : ''} · Agent 会按画像选题`,
          action: () => void sendMessage('今天读什么？请直接给我文章并带我去。'),
        }
  const saveGoal = async () => {
    setGoalSaving(true)
    try {
      const response = await api.saveLearnerGoal(goalForm)
      setGoal(response.goal)
    } finally {
      setGoalSaving(false)
    }
  }

  const openHome = (feature: 'listening' | 'writing' | 'reader') => {
    const labels = { listening: '听力听写', writing: '写作批改', reader: '泛读文章' }
    openWorkspaceUnit({
      id: `home-${feature}`,
      tier: 'home',
      label: labels[feature],
      data: { feature },
    })
    navigate('/studio')
  }

  const startSentence = () => {
    setDraft('请用五步法拆解这句：')
    window.setTimeout(() => {
      document.querySelector<HTMLTextAreaElement>('[data-agent-input]')?.focus()
    }, 60)
  }

  const launch = [
    {
      label: '推荐今日真题阅读',
      hint: '按薄弱项选一篇，直接铺开原文与题目',
      icon: Sparkles,
      action: () => void sendMessage('今天读什么？请直接给我文章并带我去。'),
    },
    {
      label: '开始今日闪卡背词',
      hint: dueWords.length ? `${dueWords.length} 个词今天到期` : '暂无到期词，可先读一篇',
      icon: Layers3,
      action: () => setFlashcardOpen(true),
    },
    {
      label: '粘贴长难句五步精析',
      hint: '把英文句子交给 Agent 拆主干、从句与修饰',
      icon: ClipboardPaste,
      action: startSentence,
    },
    {
      label: '按错题生成复习计划',
      hint: '从最近陷阱与薄弱题型生成可执行任务',
      icon: CalendarDays,
      action: () => void sendMessage('根据我最近的错题安排三天学习计划。'),
    },
    {
      label: '泛读一篇长文',
      hint: '从内容库选已发布文章，点词查义',
      icon: BookOpen,
      action: () => openHome('reader'),
    },
    {
      label: '听力听写',
      hint: '从已发布真题选一篇，逐句听写',
      icon: Headphones,
      action: () => openHome('listening'),
    },
    {
      label: '写作批改',
      hint: '打开写作画布，按最小修改反馈重写',
      icon: PenLine,
      action: () => openHome('writing'),
    },
    {
      label: '智能词测',
      hint: '选择/拼写/辨音/语境填空',
      icon: Brain,
      action: () => navigate('/vocab?tab=quiz'),
    },
  ]

  return (
    <div className="flex h-full min-h-0 flex-col bg-[#F4F6F9]">
      <div className="flex min-h-0 flex-1 items-center justify-center overflow-y-auto px-4 py-8">
        <div className="w-full max-w-3xl">
          <div className="text-center">
            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-400">
              YANYU AGENT-OS
            </p>
            <h1 className="mt-2 text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              今天，从一句话开始。
            </h1>
            <p className="mx-auto mt-2 max-w-xl text-xs leading-6 text-slate-500">
              不用先找菜单。告诉 Agent 你的目标，它会直接铺开真题、长难句、词本或计划。
            </p>
          </div>

          <div className="mx-auto mt-6 grid max-w-md grid-cols-2 gap-2">
            <div className="rounded-xl border border-slate-200 bg-white px-3 py-2.5">
              <p className="text-[9px] text-slate-400">今日到期词</p>
              <p className="mt-0.5 text-xl font-bold tabular-nums text-slate-900">{dueWords.length}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white px-3 py-2.5">
              <p className="text-[9px] text-slate-400">最紧急任务</p>
              <p className="mt-1 line-clamp-2 text-[10px] font-medium leading-4 text-slate-700">
                {urgent?.title ?? '还没有排期，让 Agent 生成一个'}
              </p>
            </div>
          </div>

          {!goal ? (
            <section className="mx-auto mt-4 max-w-3xl rounded-2xl border border-blue-200 border-l-4 border-l-blue-500 bg-white p-4 shadow-sm">
              <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
                先建立学习目标
              </p>
              <p className="mt-1 text-sm font-semibold text-slate-900">
                Agent 需要知道你的目标，才能安排今天。
              </p>
              <div className="mt-3 grid gap-2 sm:grid-cols-4">
                <label className="text-[10px] text-slate-500">
                  目标分数
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={goalForm.target_score}
                    onChange={(event) => setGoalForm((prev) => ({ ...prev, target_score: Number(event.target.value) }))}
                    className="mt-1 h-9 w-full rounded-lg border border-slate-200 px-2 text-xs text-slate-800 outline-none focus:border-slate-400"
                  />
                </label>
                <label className="text-[10px] text-slate-500">
                  考试日期
                  <input
                    type="date"
                    value={goalForm.exam_date}
                    onChange={(event) => setGoalForm((prev) => ({ ...prev, exam_date: event.target.value }))}
                    className="mt-1 h-9 w-full rounded-lg border border-slate-200 px-2 text-xs text-slate-800 outline-none focus:border-slate-400"
                  />
                </label>
                <label className="text-[10px] text-slate-500">
                  每日分钟
                  <input
                    type="number"
                    min={5}
                    max={600}
                    value={goalForm.daily_minutes}
                    onChange={(event) => setGoalForm((prev) => ({ ...prev, daily_minutes: Number(event.target.value) }))}
                    className="mt-1 h-9 w-full rounded-lg border border-slate-200 px-2 text-xs text-slate-800 outline-none focus:border-slate-400"
                  />
                </label>
                <label className="text-[10px] text-slate-500">
                  当前水平
                  <select
                    value={goalForm.current_level}
                    onChange={(event) => setGoalForm((prev) => ({ ...prev, current_level: event.target.value }))}
                    className="mt-1 h-9 w-full rounded-lg border border-slate-200 px-2 text-xs text-slate-800 outline-none focus:border-slate-400"
                  >
                    <option>基础</option>
                    <option>四级</option>
                    <option>六级</option>
                    <option>二战</option>
                  </select>
                </label>
              </div>
              <button
                type="button"
                onClick={() => void saveGoal()}
                disabled={goalSaving}
                className="mt-3 rounded-lg bg-blue-600 px-3.5 py-2 text-[11px] font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {goalSaving ? '保存中…' : '保存目标'}
              </button>
            </section>
          ) : (
            <div className="mx-auto mt-3 flex max-w-3xl flex-wrap items-center gap-2 px-1 text-[10px] text-slate-400">
              <span>目标 {goal.target_score} 分</span>
              <span>·</span>
              <span>每日 {goal.daily_minutes} 分钟</span>
              {goal.exam_date ? <><span>·</span><span>考试 {goal.exam_date}</span></> : null}
              <button type="button" onClick={() => setGoal(null)} className="ml-auto text-blue-600 hover:text-blue-800">修改目标</button>
            </div>
          )}

          <section className="mx-auto mt-4 max-w-3xl rounded-2xl border border-slate-200 border-l-4 border-l-violet-500 bg-white p-4 shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
                  今日下一步
                </p>
                <h2 className="mt-1 text-base font-semibold text-slate-900">{nextAction.label}</h2>
                <p className="mt-1 text-[11px] leading-5 text-slate-500">{nextAction.hint}</p>
              </div>
              <button
                type="button"
                onClick={nextAction.action}
                className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-slate-900 px-3.5 py-2 text-[11px] font-semibold text-white hover:bg-slate-800"
              >
                开始这一步
                <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>
            <button
              type="button"
              onClick={() => void sendMessage('根据我最近的错题、到期词和学习时间，重新安排今天的学习路径。')}
              className="mt-2 text-[10px] text-slate-400 hover:text-slate-700"
            >
              不合适？让 Agent 按今天的状态重排 →
            </button>
          </section>

          <div className="mt-5 flex items-center justify-between px-1">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
              自由练习
            </p>
            {profile?.total_attempts ? (
              <span className="text-[9px] text-slate-400">
                已练 {profile.total_attempts} 题 · 正确率 {Math.round(profile.accuracy * 100)}%
              </span>
            ) : null}
          </div>

          <div className="mt-2 grid gap-2 sm:grid-cols-2">
            {launch.map((item) => (
              <button
                key={item.label}
                type="button"
                onClick={item.action}
                className="group flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-3 text-left shadow-sm transition-all hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-50 text-slate-600 ring-1 ring-slate-200 group-hover:bg-slate-900 group-hover:text-white">
                  <item.icon className="h-4 w-4" />
                </span>
                <span className="min-w-0">
                  <span className="block text-[11px] font-semibold text-slate-800">
                    {item.label}
                  </span>
                  <span className="mt-0.5 block text-[9px] leading-4 text-slate-400">
                    {item.hint}
                  </span>
                </span>
              </button>
            ))}
          </div>

          {urgent ? (
            <button
              type="button"
              onClick={() => navigate('/studio')}
              className="mx-auto mt-3 flex items-center gap-1.5 text-[10px] text-slate-400 hover:text-slate-700"
            >
              进入全粒度精析
              <span className="text-slate-300">→</span>
            </button>
          ) : null}
        </div>
      </div>

      {messages.length === 0 ? (
        <div className="shrink-0 px-4 pb-4 pt-1 sm:px-6 sm:pb-6">
          <OmniComposer
            centered
            pills={[
              { label: '🚀 今天读哪篇？', prompt: '今天读什么？请直接给我文章并带我去。' },
              { label: '🃏 抽查到期生词', prompt: '帮我抽查今天到期的单词。' },
              { label: '📅 按近期错题排计划', prompt: '根据我最近的错题安排三天学习计划。' },
            ]}
          />
        </div>
      ) : null}
    </div>
  )
}
