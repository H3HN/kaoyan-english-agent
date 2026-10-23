import { useEffect, useRef, useState } from 'react'
import {
  ArrowUpRight,
  BookOpen,
  CalendarDays,
  GitBranch,
  Languages,
  RotateCcw,
  Send,
  Sparkles,
  Wrench,
  Target,
} from 'lucide-react'
import { Tag } from '../components/Tag'
import { api, type ChatWorkflow, type Citation, type ToolCall } from '../lib/api'
import { useAppStore } from '../store/AppStore'
import { useToast } from '../components/Toast'

interface ChatSection {
  title: string
  body?: string
  items?: string[]
  code?: string
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  intro?: string
  sections?: ChatSection[]
  tools?: ToolCall[]
  citations?: Citation[]
  source?: 'server' | 'local'
  llmUsed?: boolean
}

const CONTEXTS = [
  {
    id: '2024_en1_t1',
    label: '2024 英语一 · Text 1',
    longSentences: 3,
    questions: 2,
  },
  {
    id: '2023_en1_t1',
    label: '2023 英语一 · Text 1',
    longSentences: 4,
    questions: 1,
  },
] as const

const initialMessages: ChatMessage[] = [
  {
    id: 'welcome',
    role: 'assistant',
    intro: '把正在读的句子、做错的选项或复习计划发给我。',
  },
]

const presetPrompts = [
  {
    icon: GitBranch,
    title: '解析这个句子的从句',
    description: '按五步法拆主干与嵌套',
    prompt: '请按五步法解析这个句子的从句：What remains clear is that the technology which once seemed confined to science fiction has become part of our daily lives.',
  },
  {
    icon: Languages,
    title: '提炼本段核心词',
    description: '筛出大纲词与高频搭配',
    prompt: '请提炼这段阅读里的核心词，并区分大纲词与高频搭配：The rise of artificial intelligence has prompted both excitement and anxiety in equal measure.',
  },
  {
    icon: Target,
    title: '分析这道题的错误选项',
    description: '标注陷阱并给出排除路径',
    prompt: '请分析这道主旨题的错误选项：What is the main idea of the passage? A. AI will definitely create more jobs... D. AI will soon replace all human workers.',
  },
  {
    icon: CalendarDays,
    title: '安排本周复习计划',
    description: '按遗忘曲线排优先级',
    prompt: '请根据我的单词本，安排本周的复习计划。',
  },
  {
    icon: BookOpen,
    title: '总结段落主旨',
    description: '提炼作者态度与结构',
    prompt: '请总结这段的主旨和作者态度，并指出主旨题的定位句。',
  },
  {
    icon: BookOpen,
    title: '查一个熟词僻义',
    description: 'address / plant / subject',
    prompt: 'address、plant、subject 在考研里有哪些熟词僻义？',
  },
]

function buildReply(input: string): Omit<ChatMessage, 'id' | 'role'> {
  const text = input.toLowerCase()

  if (
    text.includes('从句') ||
    text.includes('长难句') ||
    text.includes('拆解') ||
    text.includes('句子')
  ) {
    return {
      intro:
        '这句话的难点不在词汇，而在三层嵌套。先把它拆成“主句 → 表语从句 → 定语从句”，再回头翻译。',
      sections: [
        {
          title: '主干',
          code: 'What remains clear is that the technology has become an inescapable part.',
          body: 'What remains clear 是主语从句，is 是系动词，that 引导表语从句。',
        },
        {
          title: '从句层级',
          items: [
            '主语从句：What remains clear',
            '表语从句：that the technology ... has now become ...',
            '定语从句：which once seemed confined to the realm of science fiction（修饰 technology）',
          ],
        },
        {
          title: '翻译',
          body: '有一点始终明确：这项曾经似乎只存在于科幻小说领域的技术，如今已成为我们日常生活中不可回避的一部分。',
        },
        {
          title: '考点',
          items: [
            'which 从句嵌套在表语从句内部，最容易读丢。',
            'raising ... 是现在分词作伴随状语，逻辑主语是前面整个事实。',
            '注意 part of 与 an inescapable part 的程度差异。',
          ],
        },
      ],
    }
  }

  if (text.includes('词') || text.includes('词汇')) {
    return {
      intro:
        '这段的高价值词不多，优先记能影响句意判断的形容词和动词。大纲词用绿色标出，搭配比孤立词义更重要。',
      sections: [
        {
          title: '核心词',
          items: [
            'prompt（v. 促使；引发）— prompt both excitement and anxiety',
            'revolutionize（v. 彻底改变）— revolutionize industries',
            'displacement（n. 取代；流失）— job displacement',
            'inescapable（adj. 不可回避的）— an inescapable part of daily life',
          ],
        },
        {
          title: '大纲词判断',
          body: '以上四个词均为考研大纲高频词。建议把 inescapable 与 accountability 一起记，它们常出现在科技伦理类文章。',
        },
        {
          title: '复习建议',
          body: '今天先记搭配，明天做一次无提示回忆，第 4 天再放回原句复现。不要只背中文释义。',
        },
      ],
    }
  }

  if (
    text.includes('选项') ||
    text.includes('陷阱') ||
    text.includes('主旨题') ||
    text.includes('细节题')
  ) {
    return {
      intro:
        '这类题不要从“哪个像原文”入手，而是先定题型、再定位置，最后逐项验伪。B 是全面概括，A、C、D 各有明确的陷阱类型。',
      sections: [
        {
          title: '题型与定位',
          items: [
            '题型：主旨题，要求概括全文，不是找某一句的同义替换。',
            '结构：首句提出正反两面，第二段展开，末句总结影响。',
          ],
        },
        {
          title: '错误选项',
          items: [
            'A 过于绝对：definitely 把“支持者主张”变成“确定事实”。',
            'C 缩小范围：only 把全行业影响缩成重复性任务行业。',
            'D 过于绝对：all 把 job displacement 扩大成“取代所有人类工人”。',
          ],
        },
        {
          title: '结论',
          body: 'B 同时覆盖 excitement 与 anxiety、revolutionize 与 displacement，是唯一能概括全文正反两面的选项。',
        },
      ],
    }
  }

  if (text.includes('计划') || text.includes('复习') || text.includes('单词')) {
    return {
      intro:
        '先处理到期词，再安排新词。复习计划按“到期优先、薄弱词加权、每天不超过 20 分钟”来排。',
      sections: [
        {
          title: '今天',
          items: [
            '先复习已到期的 4 个词，逐词做无提示回忆。',
            '没记住的词不延长间隔，明天再来一次。',
          ],
        },
        {
          title: '本周',
          items: [
            '周一 / 周三 / 周五各安排一次 15 分钟复习。',
            '把 ubiquitous、trajectory、accountability 放回原句复现。',
            '周末用 2024 Text 1 做一次整篇回读。',
          ],
        },
        {
          title: '原则',
          body: '复习间隔不是越短越好。记住的词拉开间隔，没记住的词缩短间隔，让时间花在真正的薄弱项上。',
        },
      ],
    }
  }

  if (
    text.includes('主旨') ||
    text.includes('总结') ||
    text.includes('段落') ||
    text.includes('态度')
  ) {
    return {
      intro:
        '这段文字不是单纯介绍 AI，而是在“兴奋”与“焦虑”之间保持张力。主旨题要选的，是能同时覆盖两面的概括项。',
      sections: [
        {
          title: '段落结构',
          items: [
            '首句总起：AI 同时引发 excitement 与 anxiety。',
            '第二句：支持者强调产业升级与新岗位。',
            '第三句：批评者警告岗位流失与重复性劳动。',
            '末句收束：技术已进入日常生活，并带来隐私、责任与能力定义的追问。',
          ],
        },
        {
          title: '一句话主旨',
          body: '人工智能在带来产业变革的同时，也引发了就业、隐私与责任层面的深层争议。',
        },
        {
          title: '作者态度',
          items: [
            '谨慎中立，不是盲目乐观，也不是全盘否定。',
            '末句的 raising questions 说明作者更关心技术带来的未解问题。',
            '主旨题优先排除 definitely、all、only 这类绝对化概括。',
          ],
        },
      ],
    }
  }

  return {
    intro:
      '可以。先把问题缩小到一个具体动作：是要读懂句子、排除选项，还是安排复习？你给我原文或题号，我会按对应的流程拆开。',
    sections: [
      {
        title: '你可以这样问',
        items: [
          '“拆解这句的从句，并标出主干。”',
          '“这道主旨题为什么不能选 C？”',
          '“把这篇文章里的生词按大纲词分类。”',
        ],
      },
      {
        title: '当前上下文',
        body: '2024 英语一 Text 1 已载入。你也可以直接粘贴新的英文段落。',
      },
    ],
  }
}

function AssistantBubble({ message }: { message: ChatMessage }) {
  return (
    <div className="max-w-[94%]">
      <div className="mb-1.5 flex items-center gap-2">
        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-800 text-white">
          <Sparkles className="h-3.5 w-3.5" />
        </span>
        <span className="text-[11px] font-semibold text-slate-700">
          研英 Agent
        </span>
      </div>
      <div className="rounded-2xl rounded-tl-md border border-slate-200 bg-slate-50/80 px-4 py-3.5">
        {message.intro ? (
          <p className="text-[13px] leading-7 text-slate-700">
            {message.intro}
          </p>
        ) : null}
        {message.sections?.map((section) => (
          <div
            key={section.title}
            className="mt-3 border-t border-slate-200/80 pt-3 first:mt-0 first:border-0 first:pt-0"
          >
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">
              {section.title}
            </p>
            {section.body ? (
              <p className="mt-1.5 text-xs leading-6 text-slate-600">
                {section.body}
              </p>
            ) : null}
            {section.items ? (
              <ul className="mt-2 space-y-1.5">
                {section.items.map((item) => (
                  <li
                    key={item}
                    className="flex items-start gap-2 text-xs leading-6 text-slate-600"
                  >
                    <span className="mt-2.5 h-1 w-1 shrink-0 rounded-full bg-slate-400" />
                    {item}
                  </li>
                ))}
              </ul>
            ) : null}
            {section.code ? (
              <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-200 bg-white px-3 py-2.5 font-serif text-[12.5px] leading-6 whitespace-pre-wrap text-slate-700">
                {section.code}
              </pre>
            ) : null}
          </div>
        ))}

        {message.tools?.length || message.citations?.length ? (
          <div className="mt-3 rounded-lg border border-slate-200 bg-white px-3 py-2.5">
            <div className="flex items-center gap-1.5">
              <Wrench className="h-2.5 w-2.5 text-slate-400" />
              <span className="text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-400">
                Tool trace
              </span>
              {message.llmUsed ? (
                <Tag tone="violet" className="ml-auto text-[9px]">
                  DeepSeek 生成
                </Tag>
              ) : message.source === 'local' ? (
                <Tag tone="amber" className="ml-auto text-[9px]">
                  本地兜底
                </Tag>
              ) : null}
            </div>
            {message.tools?.length ? (
              <div className="mt-1.5 flex flex-wrap gap-1.5">
                {message.tools.map((tool, index) => (
                  <span
                    key={`${tool.tool}-${index}`}
                    title={tool.summary}
                    className="inline-flex items-center gap-1 rounded-md bg-slate-50 px-1.5 py-1 text-[9px] font-medium text-slate-500 ring-1 ring-slate-100"
                  >
                    <code className="font-mono text-[9px]">{tool.tool}</code>
                    <span className="text-slate-300">·</span>
                    <span className="max-w-[180px] truncate">{tool.summary}</span>
                  </span>
                ))}
              </div>
            ) : null}
            {message.citations?.length ? (
              <div className="mt-2 flex flex-wrap gap-1.5 border-t border-slate-100 pt-2">
                {message.citations.slice(0, 3).map((citation) => (
                  <Tag key={citation.id} tone="emerald" title={citation.text}>
                    {citation.source}
                  </Tag>
                ))}
              </div>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages)
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const counter = useRef(0)
  const { connected, refresh } = useAppStore()
  const [contextId, setContextId] = useState<string>(CONTEXTS[0].id)
  const context = CONTEXTS.find((item) => item.id === contextId) ?? CONTEXTS[0]
  const toast = useToast()

  useEffect(() => {
    const node = scrollRef.current
    if (node) {
      node.scrollTop = node.scrollHeight
    }
  }, [messages, typing])

  const send = async (raw?: string) => {
    const text = (raw ?? input).trim()
    if (!text || typing) return

    counter.current += 1
    const userMessage: ChatMessage = {
      id: `u-${counter.current}`,
      role: 'user',
      intro: text,
    }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setTyping(true)

    try {
      const reply: ChatWorkflow = await api.chat(text, contextId)
      counter.current += 1
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${counter.current}`,
          role: 'assistant',
          intro: reply.intro,
          sections: reply.sections,
          tools: reply.tool_trace,
          citations: reply.citations,
          source: 'server',
          llmUsed: reply.llm_used,
        },
      ])
      if (
        reply.tool_trace.some((tool) => tool.tool === 'add_to_vocab_book')
      ) {
        void refresh()
      }
    } catch {
      const reply = buildReply(text)
      counter.current += 1
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${counter.current}`,
          role: 'assistant',
          ...reply,
          source: 'local',
        },
      ])
    } finally {
      setTyping(false)
    }
  }

  const clearChat = () => {
    setTyping(false)
    setMessages(initialMessages)
    toast('对话已重置。', 'info')
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
            AI COPILOT
          </p>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-900">
            AI 对话
          </h1>
        </div>
        <Tag tone="slate">{context.label}</Tag>
      </div>

      <div className="grid gap-5 lg:h-[calc(100dvh-130px)] lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="order-2 space-y-4 lg:order-1 lg:h-full lg:overflow-y-auto lg:pr-1 scrollbar-thin">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-900">快捷提问</h2>
            </div>
            <div className="mt-3 space-y-1.5">
              {presetPrompts.map((preset) => {
                const Icon = preset.icon
                return (
                  <button
                    key={preset.title}
                    type="button"
                    onClick={() => void send(preset.prompt)}
                    disabled={typing}
                    className="group flex w-full items-start gap-3 rounded-lg border border-transparent px-2.5 py-2.5 text-left transition-colors hover:border-slate-200 hover:bg-slate-50 disabled:opacity-50"
                  >
                    <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-500 group-hover:bg-white group-hover:text-slate-700">
                      <Icon className="h-3.5 w-3.5" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block text-xs font-medium text-slate-700">
                        {preset.title}
                      </span>
                    </span>
                    <ArrowUpRight className="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-300 opacity-0 transition-opacity group-hover:opacity-100" />
                  </button>
                )
              })}
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-900">
                当前上下文
              </h2>
              <Tag tone="blue">已载入</Tag>
            </div>
            <select
              value={contextId}
              onChange={(event) => {
                setContextId(event.target.value)
                toast('上下文已切换。', 'info')
              }}
              aria-label="选择上下文"
              className="mt-3 w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-xs font-medium text-slate-700 outline-none transition-colors focus:border-slate-300"
            >
              {CONTEXTS.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.label}
                </option>
              ))}
            </select>
            <div className="mt-3 flex flex-wrap gap-1.5">
              <Tag tone="emerald">长难句 {context.longSentences}</Tag>
              <Tag tone="amber">题目 {context.questions}</Tag>
            </div>
          </div>
        </aside>

        <section className="order-1 flex h-[calc(100dvh-200px)] min-h-[420px] flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm lg:order-2 lg:h-full">
          <header className="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-3.5">
            <div className="flex items-center gap-3">
              <span className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-slate-800 text-white">
                <Sparkles className="h-4 w-4" />
                <span className={`absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-white ${connected ? 'bg-emerald-400' : 'bg-amber-400'}`} />
              </span>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-sm font-semibold text-slate-900">
                    研英 Agent
                  </h2>
                  <Tag tone={connected ? 'emerald' : 'amber'} dot>
                    {connected ? '后端已连接' : '本地示例'}
                  </Tag>
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={clearChat}
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-2.5 py-1.5 text-[11px] font-medium text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-800"
            >
              <RotateCcw className="h-3 w-3" />
              清空
            </button>
          </header>

          <div
            ref={scrollRef}
            className="scrollbar-thin flex-1 space-y-5 overflow-y-auto px-4 py-5 sm:px-5"
          >
            {messages.map((message) =>
              message.role === 'assistant' ? (
                <AssistantBubble key={message.id} message={message} />
              ) : (
                <div key={message.id} className="flex justify-end">
                  <div className="max-w-[82%] rounded-2xl rounded-br-md bg-slate-800 px-4 py-3 text-[13px] leading-7 text-white shadow-sm">
                    {message.intro}
                  </div>
                </div>
              ),
            )}

            {messages.length === 1 && !typing ? (
              <div className="ml-10 flex flex-wrap gap-2">
                {[
                  {
                    label: '拆解第 4 句',
                    prompt:
                      '请按五步法拆解 2024 英语一 Text 1 的第 4 句，并标出主干与从句。',
                  },
                  {
                    label: '分析选项陷阱',
                    prompt: '请分析这道主旨题的四个选项，标注陷阱类型。',
                  },
                  {
                    label: '安排复习计划',
                    prompt: '请根据我的单词本，安排本周的复习计划。',
                  },
                ].map((item) => (
                  <button
                    key={item.label}
                    type="button"
                    onClick={() => void send(item.prompt)}
                    className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-[11px] font-medium text-slate-500 transition-colors hover:bg-slate-50 hover:text-slate-800"
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            ) : null}

            {typing ? (
              <div className="flex items-center gap-2.5">
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-800 text-white">
                  <Sparkles className="h-3.5 w-3.5" />
                </span>
                <div className="flex items-center gap-1 rounded-full border border-slate-200 bg-slate-50 px-3 py-2">
                  <span className="typing-dot h-1.5 w-1.5 rounded-full bg-slate-400" />
                  <span
                    className="typing-dot h-1.5 w-1.5 rounded-full bg-slate-400"
                    style={{ animationDelay: '0.15s' }}
                  />
                  <span
                    className="typing-dot h-1.5 w-1.5 rounded-full bg-slate-400"
                    style={{ animationDelay: '0.3s' }}
                  />
                </div>
              </div>
            ) : null}
          </div>

          <div className="border-t border-slate-200 bg-white px-4 py-3.5 sm:px-5">
            <div className="flex items-end gap-2 rounded-xl border border-slate-200 bg-slate-50/70 p-2 transition-colors focus-within:border-slate-300 focus-within:bg-white">
              <textarea
                value={input}
                onChange={(event) => setInput(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault()
                    void send()
                  }
                }}
                rows={2}
                aria-label="向 Agent 提问"
                placeholder="向 Agent 提问：解析此句从句、提炼核心词、分析选项…"
                className="max-h-32 min-h-[44px] flex-1 resize-none bg-transparent px-2 py-2 text-sm leading-6 text-slate-800 outline-none placeholder:text-slate-400"
              />
              <button
                type="button"
                onClick={() => void send()}
                disabled={!input.trim() || typing}
                aria-label="发送消息"
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-800 text-white transition-colors hover:bg-slate-900 disabled:bg-slate-200 disabled:text-slate-400"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
            <div className="mt-2 flex flex-wrap items-center justify-between gap-2 px-1">
              <p className="text-[10px] text-slate-400">
                Enter 发送 · Shift + Enter 换行
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
