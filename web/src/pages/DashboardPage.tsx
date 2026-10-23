import { useEffect, useState } from 'react'
import {
  ArrowRight,
  BookMarked,
  BookOpenCheck,
  ChevronRight,
  LibraryBig,
  MessageSquareText,
  ScanText,
  Target,
} from 'lucide-react'
import { Link } from 'react-router-dom'
import { ComparePanel } from '../components/ComparePanel'
import { FeatureCard } from '../components/FeatureCard'
import { PageHero } from '../components/PageHero'
import { SectionHeader } from '../components/SectionHeader'
import { StatCard } from '../components/StatCard'
import { Tag } from '../components/Tag'
import { api, type MetaInfo } from '../lib/api'
import { formatRelative } from '../lib/format'
import { useAppStore } from '../store/AppStore'

const features = [
  {
    to: '/sentence',
    title: '长难句拆解',
    description:
      '按五步法拆到主干、从句与修饰，英文原句保留完整语境，不做碎片化翻译。',
    icon: ScanText,
    accent: 'blue' as const,
  },
  {
    to: '/options',
    title: '选项陷阱分析',
    description:
      '左栏题干与定位句，右栏 A / B / C / D 逐项标注陷阱类型，最后回到解题路径。',
    icon: Target,
    accent: 'emerald' as const,
  },
  {
    to: '/chat',
    title: 'AI 对话',
    description:
      '把 Agent 当作随叫随到的辅导老师，围绕句子、选项与复习计划连续追问。',
    icon: MessageSquareText,
    accent: 'violet' as const,
  },
  {
    to: '/wordbook',
    title: '单词本与复习',
    description:
      '阅读中沉淀生词，按艾宾浩斯间隔安排复习，掌握度与下次复习时间一目了然。',
    icon: BookMarked,
    accent: 'amber' as const,
  },
]

export default function DashboardPage() {
  const { words, records, dueWords, connected } = useAppStore()
  const [meta, setMeta] = useState<MetaInfo | null>(null)

  useEffect(() => {
    let alive = true
    api
      .getMeta()
      .then((data) => {
        if (alive) setMeta(data)
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [])
  const averageFamiliarity =
    words.length > 0
      ? words.reduce((sum, word) => sum + word.familiarity, 0) / words.length
      : 0
  const recentRecords = records.slice(0, 5)

  return (
    <div className="space-y-6">
      <PageHero
        eyebrow="KAOYAN ENGLISH STUDIO"
        title="把阅读训练，做成可复用的工作流"
        actions={
          <>
            <Link
              to="/sentence"
              className="inline-flex items-center gap-2 rounded-lg bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 transition-colors hover:bg-slate-100"
            >
              开始拆解
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              to="/options?import=1"
              className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-white/10"
            >
              导入真题
            </Link>
            <Link
              to="/report"
              className="inline-flex items-center gap-2 rounded-lg border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-white/10"
            >
              查看学习报告
            </Link>
          </>
        }
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="真题篇章"
          value={meta ? meta.passage_count : '—'}
          hint={
            meta
              ? `${meta.question_count} 道题目 · ${meta.sentence_count} 个句子`
              : '等待后端数据'
          }
          icon={BookOpenCheck}
          accent="blue"
        />
        <StatCard
          label="大纲词汇"
          value={meta ? meta.vocab_count.toLocaleString('zh-CN') : '—'}
          hint={meta ? 'SQLite 考研词库 · 去重后' : '等待后端数据'}
          icon={LibraryBig}
          accent="cyan"
        />
        <StatCard
          label="单词本"
          value={words.length}
          hint={`平均掌握度 ${Math.round(averageFamiliarity * 100)}%`}
          icon={BookMarked}
          accent="amber"
        />
        <StatCard
          label="已练习"
          value={records.length}
          hint={connected ? 'practice_records 实时同步' : '答题记录自动沉淀'}
          icon={Target}
          accent="violet"
        />
      </div>

      {dueWords.length > 0 ? (
        <div className="flex flex-col gap-3 rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-100">
              <BookMarked className="h-4 w-4 text-amber-700" strokeWidth={1.8} />
            </span>
            <div>
              <p className="text-sm font-semibold text-amber-900">
                今天有 {dueWords.length} 个单词到期
              </p>
            </div>
          </div>
          <Link
            to="/wordbook"
            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-amber-600 px-3.5 py-2 text-xs font-semibold text-white transition-colors hover:bg-amber-700"
          >
            去复习
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      ) : null}

      <section>
        <SectionHeader
          title="核心功能"
          action={
            <Tag tone={connected ? 'emerald' : 'amber'} dot>
              {connected ? 'FastAPI 已连接' : '本地模式'}
            </Tag>
          }
        />
        <div className="grid gap-4 sm:grid-cols-2">
          {features.map((feature) => (
            <FeatureCard
              key={feature.to}
              {...feature}
              meta={
                feature.to === '/sentence'
                  ? '5 步 · 2 个工具'
                  : feature.to === '/options'
                    ? meta ? `${meta.question_count} 题 · ${meta.trap_count} 类陷阱` : '等待后端数据'
                    : feature.to === '/chat'
                      ? 'DeepSeek · 4 个工具'
                      : `${words.length} 个词 · ${dueWords.length} 待复习`
              }
            />
          ))}
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <SectionHeader
            title="定制效果预览"
            action={
              <Link
                to="/comparison"
                className="inline-flex items-center gap-1 text-xs font-medium text-slate-500 transition-colors hover:text-slate-800"
              >
                完整对比
                <ChevronRight className="h-3.5 w-3.5" />
              </Link>
            }
          />
          <ComparePanel
            className="h-full"
            left={
              <ul className="space-y-2.5">
                <li>直接翻译整句，翻完即结束</li>
                <li>选项只给“选 B”，不解释为什么</li>
                <li>生词不记录，也不安排复习</li>
              </ul>
            }
            right={
              <ul className="space-y-2.5">
                {[
                  '五步法拆主干、从句与修饰',
                  '标注陷阱类型并给出解题步骤',
                  '生词提取 → 单词本 → 复习闭环',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            }
          />
        </div>

        <div>
          <SectionHeader
            title="今日学习任务"
          />
          <div className="rounded-xl border border-slate-200 bg-white p-2 shadow-sm">
            <Link
              to="/wordbook"
              className="flex items-center gap-3 rounded-lg px-3 py-3 transition-colors hover:bg-slate-50"
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-50">
                <BookMarked className="h-4 w-4 text-amber-600" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-xs font-semibold text-slate-800">
                  复习到期单词
                </span>
                <span className="mt-0.5 block text-[11px] text-slate-400">
                  {dueWords.length > 0
                    ? `${dueWords.length} 个单词等待回忆`
                    : '今天没有到期单词'}
                </span>
              </span>
              <ChevronRight className="h-4 w-4 shrink-0 text-slate-300" />
            </Link>
            <Link
              to="/sentence"
              className="flex items-center gap-3 rounded-lg px-3 py-3 transition-colors hover:bg-slate-50"
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-50">
                <ScanText className="h-4 w-4 text-blue-600" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-xs font-semibold text-slate-800">
                  拆解 1 个长难句
                </span>
              </span>
              <ChevronRight className="h-4 w-4 shrink-0 text-slate-300" />
            </Link>
            <Link
              to="/options"
              className="flex items-center gap-3 rounded-lg px-3 py-3 transition-colors hover:bg-slate-50"
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-50">
                <Target className="h-4 w-4 text-emerald-600" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-xs font-semibold text-slate-800">
                  分析 1 道选项陷阱
                </span>
              </span>
              <ChevronRight className="h-4 w-4 shrink-0 text-slate-300" />
            </Link>          </div>
        </div>
      </div>

      <section>
        <SectionHeader
          title="最近练习"
          action={
            <Link
              to="/report"
              className="inline-flex items-center gap-1 text-xs font-medium text-slate-500 transition-colors hover:text-slate-800"
            >
              全部记录
              <ChevronRight className="h-3.5 w-3.5" />
            </Link>
          }
        />
        <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="hidden grid-cols-[1fr_100px_120px] border-b border-slate-100 bg-slate-50/70 px-5 py-3 text-[11px] font-medium text-slate-400 sm:grid">
            <span>题型</span>
            <span>结果</span>
            <span className="text-right">时间</span>
          </div>
          {recentRecords.length > 0 ? (
            recentRecords.map((record) => (
              <div
                key={record.id}
                className="flex items-center justify-between gap-3 border-b border-slate-100 px-5 py-3.5 last:border-b-0 sm:grid sm:grid-cols-[1fr_100px_120px]"
              >
                <div className="flex min-w-0 items-center gap-2">
                  <Tag tone="violet">{record.questionType}</Tag>
                  <span className="truncate text-xs text-slate-500">
                    选 {record.userAnswer} · 答案 {record.correctAnswer}
                  </span>
                </div>
                <div>
                  <Tag tone={record.isCorrect ? 'emerald' : 'red'} dot>
                    {record.isCorrect ? '正确' : '错误'}
                  </Tag>
                </div>
                <span className="hidden text-right text-[11px] text-slate-400 sm:block">
                  {formatRelative(record.time)}
                </span>
              </div>
            ))
          ) : (
            <div className="px-5 py-10 text-center text-xs text-slate-400">
              还没有练习记录，去「阅读真题训练」开始第一题。
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
