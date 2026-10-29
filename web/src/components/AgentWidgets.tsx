import { ArrowRight, BookOpenCheck, CalendarDays, CheckCircle2, Layers3, Sparkles } from 'lucide-react'
import { Tag } from './Tag'
import type { AgentWidget, ClientAction } from '../lib/api'

interface WidgetProps {
  widget: AgentWidget
  onAction: (action: ClientAction) => void
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {}
}

function asArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item) => item && typeof item === 'object') as Record<string, unknown>[] : []
}

function PassageRecommendWidget({ widget, onAction }: WidgetProps) {
  const data = asRecord(widget.data)
  return (
    <div className="rounded-xl border border-blue-100 bg-blue-50/40 p-3.5">
      <div className="flex items-start gap-2.5">
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-blue-700">
          <BookOpenCheck className="h-4 w-4" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold text-slate-900">今日推荐阅读</p>
          <p className="mt-1 text-[11px] leading-5 text-slate-600">
            {String(data.year ?? '')} {String(data.exam_type ?? '')} · Text{' '}
            {String(data.text_number ?? '')}
            {data.question_number ? ` · 第 ${String(data.question_number)} 题` : ''}
          </p>
          <p className="mt-1.5 text-[11px] leading-5 text-slate-500">
            {String(data.reason ?? '')}
          </p>
          <button
            type="button"
            onClick={() =>
              onAction({
                action_type: 'NAVIGATE_TO',
                payload: {
                  route: '/reading',
                  year: data.year,
                  exam_type: data.exam_type,
                  text_number: data.text_number,
                  question_id: data.question_id,
                },
              })
            }
            className="mt-2 inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-blue-700"
          >
            定位到题目
            <ArrowRight className="h-3 w-3" />
          </button>
        </div>
      </div>
    </div>
  )
}

function TrapDiagnosisWidget({ widget, onAction }: WidgetProps) {
  const data = asRecord(widget.data)
  const choice = String(data.user_choice ?? '')
  const correct = String(data.correct_choice ?? '')
  const trap = String(data.trap_type ?? '待分析')
  return (
    <div className="rounded-xl border border-red-100 bg-red-50/40 p-3.5">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs font-semibold text-slate-900">
          第 {String(data.question_number ?? '')} 题 · 陷阱诊断
        </p>
        <Tag tone="red">{trap}</Tag>
      </div>
      <div className="mt-2 flex flex-wrap gap-1.5 text-[11px]">
        {choice ? <Tag tone="red">{choice}: {trap}</Tag> : null}
        {correct ? <Tag tone="emerald">{correct}: 正确答案</Tag> : null}
      </div>
      <p className="mt-2 line-clamp-3 text-[11px] leading-5 text-slate-600">
        {String(data.explanation ?? '')}
      </p>
      <div className="mt-2 flex flex-wrap gap-1.5">
        <button
          type="button"
          onClick={() =>
            onAction({
              action_type: 'HIGHLIGHT_SENTENCE',
              payload: {
                sentence_id: data.sentence_id,
                sentence_text: data.sentence_text,
                question_id: data.question_id,
              },
            })
          }
          className="rounded-lg border border-red-200 bg-white px-2.5 py-1.5 text-[10px] font-medium text-red-700 hover:bg-red-50"
        >
          高亮定位句
        </button>
        <button
          type="button"
          onClick={() =>
            onAction({
              action_type: 'REVEAL_OPTION_ANALYSIS',
              payload: { question_id: data.question_id },
            })
          }
          className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[10px] font-medium text-slate-600 hover:bg-slate-50"
        >
          展开选项验伪
        </button>
      </div>
    </div>
  )
}

function VocabBatchSavedWidget({ widget, onAction }: WidgetProps) {
  const data = asRecord(widget.data)
  const words = asArray(data.words)
  return (
    <div className="rounded-xl border border-amber-100 bg-amber-50/40 p-3.5">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs font-semibold text-slate-900">生词入库摘要</p>
        <Tag tone="amber">+{String(data.added_count ?? 0)}</Tag>
      </div>
      <p className="mt-1 text-[11px] text-slate-500">
        新增 {String(data.added_count ?? 0)} · 跳过 {String(data.skipped_count ?? 0)}
      </p>
      <div className="mt-2 space-y-1.5">
        {words.map((item) => (
          <div key={String(item.word)} className="rounded-lg bg-white/80 px-2.5 py-2">
            <span className="text-[11px] font-semibold text-slate-800">
              {String(item.word)}
            </span>
            <span className="ml-1.5 text-[10px] text-slate-500">
              {String(item.meaning ?? '')}
            </span>
            {item.rare ? (
              <p className="mt-0.5 text-[10px] text-amber-700">
                熟词僻义：{String(item.rare)}
              </p>
            ) : null}
          </div>
        ))}
      </div>
      <button
        type="button"
        onClick={() =>
          onAction({ action_type: 'OPEN_FLASHCARD_DRAWER', payload: {} })
        }
        className="mt-2 inline-flex items-center gap-1.5 rounded-lg bg-amber-600 px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-amber-700"
      >
        <Layers3 className="h-3 w-3" />
        立即闪卡速记
      </button>
    </div>
  )
}

function SchedulePlanWidget({ widget, onAction }: WidgetProps) {
  const data = asRecord(widget.data)
  const tasks = asArray(data.tasks)
  return (
    <div className="rounded-xl border border-violet-100 bg-violet-50/40 p-3.5">
      <div className="flex items-center gap-2">
        <CalendarDays className="h-4 w-4 text-violet-600" />
        <p className="text-xs font-semibold text-slate-900">3 天计划预览</p>
      </div>
      <div className="mt-2 space-y-1.5">
        {tasks.map((task) => (
          <div key={`${String(task.day_label)}-${String(task.title)}`} className="flex items-start gap-2 rounded-lg bg-white/80 px-2.5 py-2">
            <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-violet-500" />
            <div className="min-w-0">
              <p className="text-[10px] font-semibold text-violet-700">
                {String(task.day_label)} · {String(task.task_type)}
              </p>
              <p className="text-[11px] leading-5 text-slate-700">{String(task.title)}</p>
            </div>
          </div>
        ))}
      </div>
      <button
        type="button"
        onClick={() =>
          onAction({ action_type: 'NAVIGATE_TO', payload: { route: '/studio' } })
        }
        className="mt-2 inline-flex items-center gap-1.5 rounded-lg border border-violet-200 bg-white px-3 py-1.5 text-[11px] font-medium text-violet-700 hover:bg-violet-50"
      >
        <Sparkles className="h-3 w-3" />
        查看计划画布
      </button>
    </div>
  )
}

const ACTION_LABELS: Partial<Record<ClientAction['action_type'], string>> = {
  NAVIGATE_TO: '在画布中打开',
  HIGHLIGHT_SENTENCE: '高亮定位句',
  REVEAL_OPTION_ANALYSIS: '展开选项验伪',
  OPEN_FLASHCARD_DRAWER: '打开闪卡',
}

export function AgentWidgetView({ widget, onAction }: WidgetProps) {
  if (widget.widget_type === 'PASSAGE_RECOMMEND') {
    return <PassageRecommendWidget widget={widget} onAction={onAction} />
  }
  if (widget.widget_type === 'TRAP_DIAGNOSIS') {
    return <TrapDiagnosisWidget widget={widget} onAction={onAction} />
  }
  if (widget.widget_type === 'VOCAB_BATCH_SAVED') {
    return <VocabBatchSavedWidget widget={widget} onAction={onAction} />
  }
  if (widget.widget_type === 'SCHEDULE_PLAN') {
    return <SchedulePlanWidget widget={widget} onAction={onAction} />
  }
  return null
}
