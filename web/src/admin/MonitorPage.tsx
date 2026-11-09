import { useCallback, useEffect, useState } from 'react'
import {
  Activity,
  AlertTriangle,
  BookMarked,
  Bot,
  Cpu,
  Loader2,
  RefreshCw,
  Target,
  X,
} from 'lucide-react'
import {
  AdminAuthError,
  adminApi,
  type MonitorCount,
  type MonitorResponse,
} from '../lib/adminApi'
import { useAdminAuth } from './AdminLayout'

const WORKFLOW_LABELS: Record<string, string> = {
  chat: 'AI 对话',
  sentence: '长难句拆解',
  options: '选项陷阱分析',
}

function countLabel(value: number): string {
  return value.toLocaleString('zh-CN')
}

export default function MonitorPage() {
  const { lock } = useAdminAuth()
  const [data, setData] = useState<MonitorResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    setLoading(true)
    adminApi
      .getMonitor()
      .then((payload) => {
        setData(payload)
        setError('')
      })
      .catch((caught) => {
        if (caught instanceof AdminAuthError) {
          lock()
          return
        }
        setError(caught instanceof Error ? caught.message : '请求失败')
      })
      .finally(() => setLoading(false))
  }, [lock])

  useEffect(() => {
    load()
  }, [load])

  const runs = data?.runs
  const practice = data?.practice
  const breakdowns = data?.breakdowns
  const wordbook = data?.wordbook
  const maxRuns = Math.max(1, ...(runs?.by_workflow.map((item) => item.count) ?? []))

  const cards = [
    {
      label: 'Agent 运行',
      value: countLabel(runs?.total ?? 0),
      hint: 'agent_runs 全部工作流',
      icon: Bot,
    },
    {
      label: '练习正确率',
      value: `${Math.round((practice?.accuracy ?? 0) * 100)}%`,
      hint: `${countLabel(practice?.correct ?? 0)} / ${countLabel(practice?.total ?? 0)} 题`,
      icon: Target,
    },
    {
      label: '拆解缓存',
      value: countLabel(breakdowns?.total ?? 0),
      hint: `LLM 生成占比 ${Math.round((breakdowns?.llm_ratio ?? 0) * 100)}%`,
      icon: Cpu,
    },
    {
      label: '单词本到期',
      value: countLabel(wordbook?.due ?? 0),
      hint: `共 ${countLabel(wordbook?.total ?? 0)} 个词`,
      icon: BookMarked,
    },
  ]

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-lg font-bold text-[#26312C]">运行监控与学情看板</h1>
          <p className="mt-1 text-[11px] text-[#8C867B]">
            聚合 Agent 工作流运行量、练习正确率、拆解缓存与单词复习状态，全部来自本地演示库。
          </p>
        </div>
        <button
          type="button"
          onClick={load}
          className="inline-flex shrink-0 items-center gap-1.5 self-start rounded-lg border border-[#D8D2C6] bg-white px-3 py-2 text-[11px] font-medium text-[#3E4A43] transition-colors hover:bg-[#F7F4EE] sm:self-auto"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? 'animate-spin' : ''}`} />
          重新加载
        </button>
      </div>

      {error ? (
        <div className="flex items-start gap-2 rounded-lg border border-[#F0D3CC] bg-[#FBEDEA] px-3.5 py-2.5 text-[11px] text-[#C05746]">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span className="flex-1">{error}</span>
          <button
            type="button"
            aria-label="关闭错误提示"
            onClick={() => setError('')}
            className="shrink-0 text-[#C05746]/60 hover:text-[#C05746]"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      ) : null}

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {cards.map(({ label, value, hint, icon: Icon }) => (
          <div
            key={label}
            className="rounded-xl border border-[#E5DFD3] bg-white px-4 py-3.5 shadow-sm"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-medium text-[#9A948A]">{label}</span>
              <Icon className="h-3.5 w-3.5 text-[#B8B1A4]" />
            </div>
            <p className="mt-1.5 text-xl font-bold tabular-nums text-[#26312C]">
              {value}
            </p>
            <p className="mt-0.5 text-[10px] text-[#B8B1A4]">{hint}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-xl border border-[#E5DFD3] bg-white shadow-sm">
          <div className="flex items-center gap-2 border-b border-[#EDE7DC] px-5 py-3">
            <Activity className="h-4 w-4 text-[#2F6F5E]" strokeWidth={1.8} />
            <span className="text-xs font-semibold text-[#26312C]">工作流运行分布</span>
          </div>
          <div className="space-y-3 px-5 py-4">
            {runs?.by_workflow.length ? (
              runs.by_workflow.map((item) => (
                <div key={item.workflow}>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-medium text-[#3E4A43]">
                      {WORKFLOW_LABELS[item.workflow] ?? item.workflow}
                    </span>
                    <span className="tabular-nums text-[#8C867B]">{item.count}</span>
                  </div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-[#F0EDE5]">
                    <div
                      className="h-full rounded-full bg-[#2F6F5E]"
                      style={{ width: `${Math.max(3, (item.count / maxRuns) * 100)}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <p className="py-6 text-center text-[11px] text-[#B8B1A4]">
                {loading ? '正在读取运行记录…' : '暂无 Agent 运行记录'}
              </p>
            )}
          </div>
        </section>

        <section className="rounded-xl border border-[#E5DFD3] bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-[#EDE7DC] px-5 py-3">
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-[#2F6F5E]" strokeWidth={1.8} />
              <span className="text-xs font-semibold text-[#26312C]">近 7 天练习量</span>
            </div>
            <span className="text-[10px] text-[#9A948A]">
              共 {countLabel(practice?.total ?? 0)} 题
            </span>
          </div>
          <div className="px-5 pb-4 pt-5">
            {practice?.daily.length ? (
              <div className="flex h-28 items-end gap-2">
                {practice.daily.map((item: MonitorCount) => {
                  const max = Math.max(1, ...practice.daily.map((day) => day.count))
                  return (
                    <div
                      key={item.date}
                      className="flex min-w-0 flex-1 flex-col items-center gap-1"
                    >
                      <span className="h-3 text-[9px] tabular-nums text-[#8C867B]">
                        {item.count > 0 ? item.count : ''}
                      </span>
                      <div
                        className="w-full rounded-t bg-[#2F6F5E]/85"
                        style={{
                          height: `${Math.max(3, (item.count / max) * 80)}px`,
                        }}
                      />
                      <span className="text-[9px] text-[#B8B1A4]">
                        {item.date.slice(5)}
                      </span>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="py-6 text-center text-[11px] text-[#B8B1A4]">
                {loading ? '正在读取练习记录…' : '暂无练习记录'}
              </p>
            )}
          </div>
        </section>
      </div>

      <section className="overflow-hidden rounded-xl border border-[#E5DFD3] bg-white shadow-sm">
        <div className="flex items-center gap-2 border-b border-[#EDE7DC] px-5 py-3">
          <Target className="h-4 w-4 text-[#2F6F5E]" strokeWidth={1.8} />
          <span className="text-xs font-semibold text-[#26312C]">分题型正确率</span>
        </div>
        <div className="hidden grid-cols-[1fr_0.5fr_0.6fr_2fr] gap-3 border-b border-[#EDE7DC] bg-[#FCFBF8] px-5 py-2 text-[10px] font-medium text-[#9A948A] sm:grid">
          <span>题型</span>
          <span>题数</span>
          <span>正确率</span>
          <span>分布</span>
        </div>
        {practice?.by_type.length ? (
          practice.by_type.map((item) => (
            <div
              key={item.type}
              className="flex flex-col gap-1.5 border-b border-[#EDE7DC] px-5 py-3 last:border-b-0 sm:grid sm:grid-cols-[1fr_0.5fr_0.6fr_2fr] sm:items-center sm:gap-3"
            >
              <span className="text-[11px] font-medium text-[#3E4A43]">{item.type}</span>
              <span className="text-[10px] tabular-nums text-[#6B6559]">{item.total}</span>
              <span
                className={`text-[10px] font-semibold tabular-nums ${
                  item.accuracy >= 0.7 ? 'text-[#2F6F5E]' : 'text-[#C05746]'
                }`}
              >
                {Math.round(item.accuracy * 100)}%
              </span>
              <div className="h-1.5 overflow-hidden rounded-full bg-[#F0EDE5]">
                <div
                  className={`h-full rounded-full ${
                    item.accuracy >= 0.7 ? 'bg-[#2F6F5E]' : 'bg-[#C05746]'
                  }`}
                  style={{ width: `${Math.max(3, item.accuracy * 100)}%` }}
                />
              </div>
            </div>
          ))
        ) : (
          <p className="px-5 py-8 text-center text-[11px] text-[#B8B1A4]">
            {loading ? (
              <span className="inline-flex items-center gap-1.5">
                <Loader2 className="h-3 w-3 animate-spin" /> 正在聚合…
              </span>
            ) : (
              '暂无练习记录'
            )}
          </p>
        )}
      </section>

      <p className="text-[10px] text-[#9A948A]">
        数据来源：agent_runs / practice_records / sentence_breakdowns / user_vocab_book
      </p>
    </div>
  )
}