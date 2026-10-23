import { useEffect, useMemo, useState } from 'react'
import {
  BookOpen,
  BookOpenCheck,
  GitBranch,
  Layers,
  Search,
  Target,
} from 'lucide-react'
import { EmptyState } from '../components/EmptyState'
import { PageHero } from '../components/PageHero'
import { SectionHeader } from '../components/SectionHeader'
import { StatCard } from '../components/StatCard'
import { Tag, toneStyles, type Tone } from '../components/Tag'
import { api, type MetaInfo, type RareWord } from '../lib/api'
import {
  METHODOLOGY,
  QUESTION_TYPES,
  TRAP_TYPES,
} from '../data/content'

type Tab = 'types' | 'traps' | 'methods'

const borderMap: Record<Tone, string> = {
  blue: 'border-l-blue-500',
  emerald: 'border-l-emerald-500',
  cyan: 'border-l-cyan-500',
  amber: 'border-l-amber-500',
  violet: 'border-l-violet-500',
  red: 'border-l-red-500',
  slate: 'border-l-slate-300',
}

export default function KnowledgePage() {
  const [tab, setTab] = useState<Tab>('types')
  const [query, setQuery] = useState('')
  const [meta, setMeta] = useState<MetaInfo | null>(null)
  const [rareWords, setRareWords] = useState<RareWord[]>([])
  const keyword = query.trim().toLowerCase()

  useEffect(() => {
    let alive = true
    api
      .getKnowledge()
      .then((data) => {
        if (!alive) return
        setMeta(data.meta)
        setRareWords(data.rare_words)
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [])

  const filteredTypes = useMemo(
    () =>
      QUESTION_TYPES.filter((item) =>
        [item.name, item.desc, item.signal, ...item.steps]
          .join(' ')
          .toLowerCase()
          .includes(keyword),
      ),
    [keyword],
  )
  const filteredTraps = useMemo(
    () =>
      TRAP_TYPES.filter((item) =>
        [item.name, item.desc, item.signal]
          .join(' ')
          .toLowerCase()
          .includes(keyword),
      ),
    [keyword],
  )
  const filteredMethods = useMemo(
    () =>
      METHODOLOGY.filter((item) =>
        [item.name, item.desc, ...item.steps]
          .join(' ')
          .toLowerCase()
          .includes(keyword),
      ),
    [keyword],
  )

  const currentCount =
    tab === 'types'
      ? filteredTypes.length
      : tab === 'traps'
        ? filteredTraps.length
        : filteredMethods.length

  return (
    <div className="space-y-6">
      <PageHero
        eyebrow="DOMAIN KNOWLEDGE"
        title="领域知识库"
        subtitle="Agent 的判断不是凭空来的。题型、陷阱、拆解方法都沉淀在这里，成为每一次回答的参照系。"
      />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          label="大纲词汇"
          value={meta ? meta.vocab_count.toLocaleString('zh-CN') : '1,678'}
          hint={meta ? 'SQLite 考研词库 · 去重后' : '当前演示词库'}
          icon={BookOpenCheck}
          accent="blue"
        />
        <StatCard
          label="内置真题"
          value={meta ? `${meta.passage_count} 篇` : '2 篇'}
          hint="2023 / 2024 英语一"
          icon={BookOpen}
          accent="emerald"
        />
        <StatCard
          label="题型分类"
          value={QUESTION_TYPES.length}
          hint="细节 / 主旨 / 推理 / 词义 / 态度"
          icon={Target}
          accent="violet"
        />
        <StatCard
          label="陷阱类型"
          value={meta ? meta.trap_count : TRAP_TYPES.length}
          hint="核心六类 + 两个细分"
          icon={Layers}
          accent="amber"
        />
      </div>

      {rareWords.length > 0 ? (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <div className="flex items-center gap-2">
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-50">
                  <BookOpenCheck className="h-3.5 w-3.5 text-amber-600" />
                </span>
                <h2 className="text-sm font-semibold text-slate-900">
                  熟词僻义 · 高频样例
                </h2>
                <Tag tone="amber">SQLite</Tag>
              </div>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-400">
                同一个词，考研阅读里可能考第二个意思。先按语境判断，再背第一释义。
              </p>
            </div>
            <span className="text-[10px] text-slate-400">
              共 {rareWords.length} 个样例
            </span>
          </div>
          <div className="mt-4 grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {rareWords.map((item) => (
              <div
                key={item.word}
                className="rounded-lg border border-slate-100 bg-slate-50/60 p-3"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-serif text-sm font-semibold text-slate-900">
                    {item.word}
                  </span>
                  <Tag tone="amber">{item.level}</Tag>
                </div>
                <p className="mt-1 line-clamp-1 text-[10px] text-slate-500">
                  {item.basic_meaning}
                </p>
                <p className="mt-1.5 text-[11px] leading-relaxed text-amber-800">
                  {item.rare_meaning}
                </p>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap gap-1.5">
            {(
              [
                { id: 'types', label: '题型方法论', count: QUESTION_TYPES.length },
                { id: 'traps', label: '陷阱类型', count: TRAP_TYPES.length },
                { id: 'methods', label: '拆解方法', count: METHODOLOGY.length },
              ] as const
            ).map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => setTab(item.id)}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3.5 py-2 text-xs font-medium transition-colors ${
                  tab === item.id
                    ? 'bg-slate-800 text-white'
                    : 'bg-slate-50 text-slate-500 hover:bg-slate-100 hover:text-slate-800'
                }`}
                aria-pressed={tab === item.id}
              >
                {item.label}
                <span
                  className={`rounded-full px-1.5 py-0.5 text-[9px] ${
                    tab === item.id
                      ? 'bg-white/15 text-white'
                      : 'bg-white text-slate-400'
                  }`}
                >
                  {item.count}
                </span>
              </button>
            ))}
          </div>

          <div className="relative w-full lg:w-[300px]">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              aria-label="搜索知识库"
              placeholder="搜索题型、陷阱或方法…"
              className="w-full rounded-lg border border-slate-200 bg-slate-50/60 py-2.5 pl-9 pr-3 text-xs text-slate-700 outline-none transition-colors placeholder:text-slate-400 focus:border-slate-300 focus:bg-white"
            />
          </div>
        </div>
        <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-3 text-[10px] text-slate-400">
          <span>当前显示 {currentCount} 条知识条目</span>
          <span>SQLite 知识库 · 可继续导入全量真题</span>
        </div>
      </div>

      {tab === 'types' ? (
        <section>
          <SectionHeader
            title="题型方法论"
            description="先判断题目在问什么，再决定去哪里找答案。"
          />
          {filteredTypes.length > 0 ? (
            <div className="grid gap-4 lg:grid-cols-2">
              {filteredTypes.map((item) => {
                const tone: Tone = 'cyan'
                return (
                  <div
                    key={item.name}
                    className={`rounded-xl border border-slate-200 border-l-4 bg-white p-5 shadow-sm ${borderMap[tone]}`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span
                          className={`flex h-8 w-8 items-center justify-center rounded-lg ${toneStyles[tone].soft}`}
                        >
                          <Target
                            className={`h-4 w-4 ${toneStyles[tone].icon}`}
                          />
                        </span>
                        <h3 className="text-sm font-semibold text-slate-900">
                          {item.name}
                        </h3>
                      </div>
                      <Tag tone={tone}>题型</Tag>
                    </div>
                    <p className="mt-3 text-xs leading-relaxed text-slate-500">
                      {item.desc}
                    </p>
                    <div className="mt-3 rounded-lg bg-slate-50 px-3 py-2">
                      <p className="text-[10px] font-medium uppercase tracking-[0.12em] text-slate-400">
                        题干信号
                      </p>
                      <p className="mt-1 font-mono text-[10px] leading-relaxed text-slate-500">
                        {item.signal}
                      </p>
                    </div>
                    <ol className="mt-3 space-y-1.5">
                      {item.steps.map((step, stepIndex) => (
                        <li
                          key={step}
                          className="flex items-start gap-2 text-[11px] leading-relaxed text-slate-600"
                        >
                          <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded bg-white text-[9px] font-bold text-slate-400 ring-1 ring-slate-200">
                            {stepIndex + 1}
                          </span>
                          {step}
                        </li>
                      ))}
                    </ol>
                  </div>
                )
              })}
            </div>
          ) : (
            <EmptyState
              icon={Search}
              title="没有匹配的题型"
              description="换一个关键词，或清空搜索查看全部题型。"
            />
          )}
        </section>
      ) : null}

      {tab === 'traps' ? (
        <section>
          <SectionHeader
            title="陷阱类型"
            description="干扰项不是随机编的，常见形态就这几类。"
          />
          {filteredTraps.length > 0 ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredTraps.map((item) => (
                <div
                  key={item.name}
                  className={`rounded-xl border border-slate-200 border-l-4 bg-white p-5 shadow-sm ${borderMap[item.tone]}`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-sm font-semibold text-slate-900">
                      {item.name}
                    </h3>
                    <Tag tone={item.tone} dot>
                      干扰项
                    </Tag>
                  </div>
                  <p className="mt-2.5 text-xs leading-relaxed text-slate-500">
                    {item.desc}
                  </p>
                  <div className="mt-3 border-t border-slate-100 pt-2.5">
                    <p className="text-[10px] text-slate-400">常见信号</p>
                    <p className="mt-1 text-[11px] leading-relaxed text-slate-600">
                      {item.signal}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={Search}
              title="没有匹配的陷阱类型"
              description="试试“范围”“偷换”“无中生有”等关键词。"
            />
          )}
        </section>
      ) : null}

      {tab === 'methods' ? (
        <section>
          <SectionHeader
            title="拆解方法"
            description="两套固定流程，分别处理句子与选项。"
          />
          {filteredMethods.length > 0 ? (
            <div className="grid gap-4 lg:grid-cols-2">
              {filteredMethods.map((item) => (
                <div
                  key={item.name}
                  className="rounded-xl border border-slate-200 border-l-4 border-l-blue-500 bg-white p-5 shadow-sm"
                >
                  <div className="flex items-center gap-2">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50">
                      <GitBranch className="h-4 w-4 text-blue-600" />
                    </span>
                    <h3 className="text-sm font-semibold text-slate-900">
                      {item.name}
                    </h3>
                  </div>
                  <p className="mt-3 text-xs leading-relaxed text-slate-500">
                    {item.desc}
                  </p>
                  <div className="mt-4 space-y-2">
                    {item.steps.map((step, index) => (
                      <div
                        key={step}
                        className="flex items-start gap-3 rounded-lg bg-slate-50/70 px-3 py-2.5"
                      >
                        <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-white text-[9px] font-bold text-slate-400 ring-1 ring-slate-200">
                          {index + 1}
                        </span>
                        <p className="text-[11px] leading-relaxed text-slate-600">
                          {step}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={Search}
              title="没有匹配的方法"
              description="清空搜索，查看完整的两套拆解流程。"
            />
          )}
        </section>
      ) : null}
    </div>
  )
}
