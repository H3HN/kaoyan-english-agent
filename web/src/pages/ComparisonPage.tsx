import {
  ArrowRight,
  BookOpenCheck,
  GitCompareArrows,
  Layers,
  ListChecks,
  MessageSquareText,
  Target,
  Workflow,
  X,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { ComparePanel } from '../components/ComparePanel'
import { FeatureCard } from '../components/FeatureCard'
import { PageHero } from '../components/PageHero'
import { SectionHeader } from '../components/SectionHeader'
import { StatCard } from '../components/StatCard'
import { Tag } from '../components/Tag'
import { COMPARISONS } from '../data/content'

const methods = [
  {
    to: '/knowledge',
    title: '领域知识库',
    description:
      '大纲词汇、真题、题型方法论、语法体系与陷阱分类，构成 Agent 作答的边界。',
    icon: BookOpenCheck,
    accent: 'blue' as const,
  },
  {
    to: '/chat',
    title: '提示词设计',
    description:
      '角色设定、拆解流程、输出格式都写进系统提示词，避免回答漂移。',
    icon: MessageSquareText,
    accent: 'violet' as const,
  },
  {
    to: '/sentence',
    title: '工具调用',
    description:
      '长难句拆解、陷阱识别、单词本与艾宾浩斯复习，各自负责一个明确动作。',
    icon: Target,
    accent: 'emerald' as const,
  },
  {
    to: '/report',
    title: '流程编排',
    description:
      '导入 → 拆解 → 分析 → 提取 → 复习 → 报告，形成完整学习闭环。',
    icon: Workflow,
    accent: 'amber' as const,
  },
]

export default function ComparisonPage() {
  return (
    <div className="space-y-6">
      <PageHero
        eyebrow="CUSTOMIZATION PROOF"
        title="定制效果对比"
        subtitle="同一个问题，通用模型给结论，领域 Agent 给路径。定制不是换一个更大的模型，而是把领域方法写进流程。"
        actions={
          <Link
            to="/chat"
            className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-white/10"
          >
            去问 Agent
            <ArrowRight className="h-4 w-4" />
          </Link>
        }
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="对照场景"
          value="3"
          hint="拆解 / 选项 / 生词"
          icon={GitCompareArrows}
          accent="blue"
        />
        <StatCard
          label="拆解路径"
          value="5 步"
          hint="找主干到标语法点"
          icon={ListChecks}
          accent="emerald"
        />
        <StatCard
          label="陷阱类型"
          value="6 类"
          hint="范围 / 偷换 / 反义 / 无据"
          icon={Layers}
          accent="amber"
        />
        <StatCard
          label="学习闭环"
          value="1 条"
          hint="从阅读到复习"
          icon={Workflow}
          accent="violet"
        />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl">
            <div className="flex items-center gap-2">
              <Tag tone="violet">WHY CUSTOM</Tag>
              <span className="text-[11px] text-slate-400">
                通用能力 ≠ 领域方法
              </span>
            </div>
            <h2 className="mt-3 text-lg font-semibold tracking-tight text-slate-900">
              差别不在“知不知道”，而在“按不按流程做”
            </h2>
            <p className="mt-1.5 text-xs leading-relaxed text-slate-500">
              通用模型可以翻译对一句话，但不一定会主动剥离从句；可以选对答案，但不一定说得清另外三项错在哪。定制 Agent 的价值，是把老师的检查顺序固定下来。
            </p>
          </div>
          <div className="grid shrink-0 grid-cols-2 gap-2 lg:w-[320px]">
            <div className="rounded-lg bg-red-50 px-3.5 py-3">
              <p className="text-[10px] font-medium text-red-500">通用模型</p>
              <p className="mt-1 text-xs font-semibold text-red-800">
                给结论
              </p>
            </div>
            <div className="rounded-lg bg-emerald-50 px-3.5 py-3">
              <p className="text-[10px] font-medium text-emerald-500">
                定制 Agent
              </p>
              <p className="mt-1 text-xs font-semibold text-emerald-800">
                给路径
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {COMPARISONS.map((scenario, index) => (
          <section key={scenario.id}>
            <SectionHeader
              title={`场景 ${index + 1} · ${scenario.title}`}
              description={scenario.question}
              action={
                <span className="text-[11px] text-slate-400">
                  左：通用回答 / 右：定制路径
                </span>
              }
            />
            <ComparePanel
              left={
                <div className="flex h-full flex-col">
                  <p>{scenario.generic}</p>
                  <div className="mt-5 rounded-lg border border-red-100 bg-red-50/50 px-3.5 py-3">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-red-500">
                      缺失的检查项
                    </p>
                    <ul className="mt-2 space-y-1.5">
                      {scenario.genericGaps.map((gap) => (
                        <li
                          key={gap}
                          className="flex items-start gap-2 text-[11px] leading-relaxed text-slate-600"
                        >
                          <X className="mt-0.5 h-3 w-3 shrink-0 text-red-400" />
                          {gap}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <p className="mt-auto pt-5 text-[11px] leading-relaxed text-slate-400">
                    {scenario.genericVerdict}
                  </p>
                </div>
              }
              right={
                <div className="space-y-2.5">
                  {scenario.custom.map((row) => (
                    <div
                      key={row.label}
                      className="rounded-lg border border-emerald-100 bg-emerald-50/40 px-3.5 py-2.5"
                    >
                      <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-emerald-700">
                        {row.label}
                      </p>
                      {Array.isArray(row.value) ? (
                        <div className="mt-1.5 flex flex-wrap gap-1.5">
                          {row.value.map((value) => (
                            <span
                              key={value}
                              className="rounded-md bg-white px-2 py-1 text-[11px] leading-relaxed text-slate-600 ring-1 ring-emerald-100"
                            >
                              {value}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p className="mt-1.5 text-xs leading-relaxed text-slate-600">
                          {row.value}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              }
            />
          </section>
        ))}
      </div>

      <section>
        <SectionHeader
          title="定制方法"
          description="四个层面共同作用，才让回答稳定落在考研阅读的语境里。"
        />
        <div className="grid gap-4 sm:grid-cols-2">
          {methods.map((method) => (
            <FeatureCard key={method.to} {...method} />
          ))}
        </div>
      </section>
    </div>
  )
}
