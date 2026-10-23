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
    meta: '5,064 词 · 8 切片',
  },
  {
    to: '/chat',
    title: '提示词设计',
    description:
      '角色设定、拆解流程、输出格式都写进系统提示词，避免回答漂移。',
    icon: MessageSquareText,
    accent: 'violet' as const,
    meta: 'System Prompt',
  },
  {
    to: '/sentence',
    title: '工具调用',
    description:
      '长难句拆解、陷阱识别、单词本与艾宾浩斯复习，各自负责一个明确动作。',
    icon: Target,
    accent: 'emerald' as const,
    meta: '4 Tools',
  },
  {
    to: '/report',
    title: '流程编排',
    description:
      '导入 → 拆解 → 分析 → 提取 → 复习 → 报告，形成完整学习闭环。',
    icon: Workflow,
    accent: 'amber' as const,
    meta: '3 Workflows',
  },
]

export default function ComparisonPage() {
  return (
    <div className="space-y-6">
      <PageHero
        eyebrow="CUSTOMIZATION PROOF"
        title="定制效果对比"
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
          value="8 类"
          hint="核心六类 + 两个细分"
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

      <div className="space-y-6">
        {COMPARISONS.map((scenario, index) => (
          <section key={scenario.id}>
            <SectionHeader title={`场景 ${index + 1} · ${scenario.title}`} />
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
