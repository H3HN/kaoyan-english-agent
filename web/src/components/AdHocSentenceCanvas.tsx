import { useEffect, useRef, useState } from 'react'
import { BookOpen, Braces, CheckCircle2, GitBranch, Languages, Lightbulb, Link2, MessageSquarePlus, Sparkles } from 'lucide-react'
import type { AdHocSentenceData } from '../lib/api'
import { Tag } from './Tag'

const STEP_STYLES = [
  { n: '01', title: '找主干', icon: Braces, bar: 'border-l-blue-500', iconTone: 'bg-blue-50 text-blue-600' },
  { n: '02', title: '剥离从句', icon: GitBranch, bar: 'border-l-violet-500', iconTone: 'bg-violet-50 text-violet-600' },
  { n: '03', title: '划分修饰', icon: Link2, bar: 'border-l-amber-500', iconTone: 'bg-amber-50 text-amber-600' },
  { n: '04', title: '逐层翻译', icon: Languages, bar: 'border-l-emerald-500', iconTone: 'bg-emerald-50 text-emerald-600' },
  { n: '05', title: '词汇与语法', icon: Lightbulb, bar: 'border-l-cyan-500', iconTone: 'bg-cyan-50 text-cyan-600' },
]

function EmptyLine({ text }: { text: string }) {
  return <p className="text-sm leading-7 text-slate-400">{text}</p>
}

export function AdHocSentenceCanvas({
  data,
  status = 'draft',
  onSave,
  onOpenLibrary,
  onAddWord,
  onAskAgent,
  markedWords = new Set<string>(),
}: {
  data: AdHocSentenceData
  status?: 'draft' | 'saved' | 'featured'
  onSave?: () => void
  onOpenLibrary?: () => void
  onAddWord?: (word: string) => Promise<void> | void
  onAskAgent?: (word: string) => void
  markedWords?: Set<string>
}) {
  const sentenceRef = useRef<HTMLDivElement>(null)
  const [popover, setPopover] = useState<{ text: string; x: number; y: number } | null>(null)
  const clauses = data.step2_clauses ?? []
  const modifiers = data.step3_modifiers ?? []
  const vocab = data.step5_vocab_and_grammar?.vocabulary ?? []
  const grammar = data.step5_vocab_and_grammar?.grammar ?? []
  const examPoints = data.step5_vocab_and_grammar?.exam_points ?? []

  return (
    <div className="space-y-3">
      <section className="rounded-2xl bg-slate-900 px-5 py-4 text-white shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
              {status === 'featured'
                ? 'FEATURED SENTENCE · 真题精选'
                : status === 'saved'
                  ? 'SAVED SENTENCE · 已归档'
                  : 'AD-HOC SENTENCE · 实时精析'}
            </p>
            <h1 className="mt-1 text-xl font-bold tracking-tight">长难句五步精析台</h1>
            <p className="mt-1 text-[11px] text-slate-300">
              {data.source_label} · {data.word_count ?? 0} 词
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            {status === 'draft' ? (
              <span className="inline-flex items-center gap-1 rounded-full bg-amber-400/15 px-2.5 py-1 text-[10px] font-medium text-amber-200">
                ✨ 实时精析草稿
              </span>
            ) : null}
            {status === 'saved' ? (
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-400/15 px-2.5 py-1 text-[10px] font-medium text-emerald-200">
                <CheckCircle2 className="h-3 w-3" /> 已归档长难句
              </span>
            ) : null}
            {status === 'featured' ? (
              <span className="inline-flex items-center gap-1 rounded-full bg-blue-400/15 px-2.5 py-1 text-[10px] font-medium text-blue-200">
                🔥 真题精选
              </span>
            ) : null}
            {status !== 'saved' && onSave ? (
              <button
                type="button"
                onClick={onSave}
                className="rounded-lg bg-white px-2.5 py-1.5 text-[10px] font-semibold text-slate-900 hover:bg-slate-100"
              >
                📌 存入长难句库
              </button>
            ) : null}
            {onOpenLibrary ? (
              <button
                type="button"
                onClick={onOpenLibrary}
                className="rounded-lg border border-white/15 bg-white/5 px-2.5 py-1.5 text-[10px] text-slate-200 hover:bg-white/10"
              >
                📚 句库抽屉
              </button>
            ) : null}
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-slate-900 text-white">
            <BookOpen className="h-3.5 w-3.5" />
          </span>
          <p className="text-sm font-semibold text-slate-900">原文</p>
          <Tag tone="slate">外源输入</Tag>
        </div>
        <div
          ref={sentenceRef}
          onMouseUp={() => {
            const selection = window.getSelection()
            const selected = selection?.toString().trim() ?? ''
            if (!selected || !selection?.rangeCount || !sentenceRef.current?.contains(selection.anchorNode)) {
              return
            }
            const rect = selection.getRangeAt(0).getBoundingClientRect()
            setPopover({
              text: selected,
              x: rect.left + rect.width / 2,
              y: rect.top - 8,
            })
          }}
          className="mt-3 select-text font-serif text-[16px] leading-8 text-slate-800"
        >
          {data.sentence_en.split(/(\b[A-Za-z][A-Za-z'’\-]*\b)/g).map((token, index) => {
            const isWord = /^[A-Za-z]/.test(token)
            const marked = isWord && markedWords.has(token.toLowerCase())
            return isWord ? (
              <span
                key={`${token}-${index}`}
                onClick={(event) => {
                  event.stopPropagation()
                  const rect = (event.currentTarget as HTMLElement).getBoundingClientRect()
                  setPopover({ text: token, x: rect.left + rect.width / 2, y: rect.top - 8 })
                }}
                className={`cursor-pointer rounded-sm transition-colors hover:bg-slate-100 ${
                  marked ? 'border-b-2 border-dashed border-amber-400 bg-amber-50/70' : ''
                }`}
              >
                {token}
              </span>
            ) : (
              <span key={`${token}-${index}`}>{token}</span>
            )
          })}
        </div>
      </section>

      <div className="grid gap-3 lg:grid-cols-2">
        <section className={`rounded-xl border border-slate-200 border-l-4 ${STEP_STYLES[0].bar} bg-white p-4 shadow-sm lg:col-span-2`}>
          <div className="flex items-center gap-2">
            <span className={`flex h-7 w-7 items-center justify-center rounded-lg ${STEP_STYLES[0].iconTone}`}>
              <Braces className="h-3.5 w-3.5" />
            </span>
            <span className="text-[10px] font-semibold tracking-[0.14em] text-slate-400">{STEP_STYLES[0].n}</span>
            <h2 className="text-sm font-semibold text-slate-900">{STEP_STYLES[0].title}</h2>
          </div>
          <p className="mt-2 whitespace-pre-line text-[14.5px] leading-7 text-slate-700">
            {data.step1_trunk || '未识别出主干'}
          </p>
        </section>

        <section className={`rounded-xl border border-slate-200 border-l-4 ${STEP_STYLES[1].bar} bg-white p-4 shadow-sm`}>
          <div className="flex items-center gap-2">
            <span className={`flex h-7 w-7 items-center justify-center rounded-lg ${STEP_STYLES[1].iconTone}`}>
              <GitBranch className="h-3.5 w-3.5" />
            </span>
            <span className="text-[10px] font-semibold tracking-[0.14em] text-slate-400">{STEP_STYLES[1].n}</span>
            <h2 className="text-sm font-semibold text-slate-900">{STEP_STYLES[1].title}</h2>
          </div>
          <div className="mt-2 space-y-2.5">
            {clauses.length ? clauses.map((item, index) => (
              <div key={`${item.text}-${index}`} className="rounded-lg bg-slate-50/80 p-2.5">
                <div className="flex flex-wrap items-center gap-1.5">
                  <Tag tone="violet">{item.label}</Tag>
                  <span className="text-[14.5px] font-medium text-slate-800">{item.text}</span>
                </div>
                <p className="mt-1 text-[13px] leading-6 text-slate-500">{item.note}</p>
              </div>
            )) : <EmptyLine text="未识别到独立从句。" />}
          </div>
        </section>

        <section className={`rounded-xl border border-slate-200 border-l-4 ${STEP_STYLES[2].bar} bg-white p-4 shadow-sm`}>
          <div className="flex items-center gap-2">
            <span className={`flex h-7 w-7 items-center justify-center rounded-lg ${STEP_STYLES[2].iconTone}`}>
              <Link2 className="h-3.5 w-3.5" />
            </span>
            <span className="text-[10px] font-semibold tracking-[0.14em] text-slate-400">{STEP_STYLES[2].n}</span>
            <h2 className="text-sm font-semibold text-slate-900">{STEP_STYLES[2].title}</h2>
          </div>
          <div className="mt-2 space-y-2.5">
            {modifiers.length ? modifiers.map((item, index) => (
              <div key={`${item.text}-${index}`} className="rounded-lg bg-slate-50/80 p-2.5">
                <div className="flex flex-wrap items-center gap-1.5">
                  <Tag tone="amber">{item.label}</Tag>
                  <span className="text-[14.5px] font-medium text-slate-800">{item.text}</span>
                </div>
                <p className="mt-1 text-[13px] leading-6 text-slate-500">{item.note}</p>
              </div>
            )) : <EmptyLine text="未识别到独立修饰成分。" />}
          </div>
        </section>

        <section className={`rounded-xl border border-slate-200 border-l-4 ${STEP_STYLES[3].bar} bg-white p-4 shadow-sm lg:col-span-2`}>
          <div className="flex items-center gap-2">
            <span className={`flex h-7 w-7 items-center justify-center rounded-lg ${STEP_STYLES[3].iconTone}`}>
              <Languages className="h-3.5 w-3.5" />
            </span>
            <span className="text-[10px] font-semibold tracking-[0.14em] text-slate-400">{STEP_STYLES[3].n}</span>
            <h2 className="text-sm font-semibold text-slate-900">{STEP_STYLES[3].title}</h2>
          </div>
          <p className="mt-2 text-[15px] leading-7 text-slate-700">
            {data.step4_translation || '暂未生成翻译。'}
          </p>
          {data.step4_translation_layers?.length ? (
            <div className="mt-2 space-y-1.5">
              {data.step4_translation_layers.map((layer) => (
                <p key={layer} className="text-[13px] leading-6 text-slate-500">· {layer}</p>
              ))}
            </div>
          ) : null}
        </section>

        <section className={`rounded-xl border border-slate-200 border-l-4 ${STEP_STYLES[4].bar} bg-white p-4 shadow-sm lg:col-span-2`}>
          <div className="flex items-center gap-2">
            <span className={`flex h-7 w-7 items-center justify-center rounded-lg ${STEP_STYLES[4].iconTone}`}>
              <Lightbulb className="h-3.5 w-3.5" />
            </span>
            <span className="text-[10px] font-semibold tracking-[0.14em] text-slate-400">{STEP_STYLES[4].n}</span>
            <h2 className="text-sm font-semibold text-slate-900">{STEP_STYLES[4].title}</h2>
          </div>
          <div className="mt-2 grid gap-3 lg:grid-cols-2">
            <div>
              <p className="text-sm font-semibold text-slate-900">核心生词</p>
              <div className="mt-2 space-y-2">
                {vocab.length ? vocab.map((item) => (
                  <div key={item.word} className="rounded-lg bg-amber-50/70 px-3 py-2">
                    <div className="flex flex-wrap items-center gap-1.5">
                      <span className="text-sm font-semibold text-slate-900">{item.word}</span>
                      <Tag tone="amber">大纲词</Tag>
                    </div>
                    <p className="mt-0.5 text-[13px] leading-6 text-slate-600">{item.meaning}</p>
                    {item.rare_meaning ? (
                      <p className="text-[12px] leading-5 text-amber-700">熟词僻义：{item.rare_meaning}</p>
                    ) : null}
                  </div>
                )) : <EmptyLine text="未命中大纲核心词。" />}
              </div>
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900">语法点</p>
              <div className="mt-2 space-y-2">
                {grammar.length ? grammar.map((item) => (
                  <div key={item.name} className="rounded-lg bg-violet-50/70 px-3 py-2">
                    <p className="text-sm font-medium text-slate-800">{item.name}</p>
                    <p className="mt-0.5 text-[13px] leading-6 text-slate-600">{item.note}</p>
                  </div>
                )) : <EmptyLine text="暂无额外语法标注。" />}
              </div>
              {examPoints.length ? (
                <div className="mt-2 rounded-lg border border-dashed border-slate-200 px-3 py-2">
                  <p className="text-[10px] font-semibold text-slate-400">命题点</p>
                  <p className="mt-1 text-[13px] leading-6 text-slate-600">{examPoints.join('；')}</p>
                </div>
              ) : null}
            </div>
          </div>
        </section>
      </div>

      {popover ? (
        <div
          className="fixed z-[80] flex -translate-x-1/2 -translate-y-full items-center gap-1 rounded-lg bg-slate-900 px-1.5 py-1 text-white shadow-xl"
          style={{ left: popover.x, top: popover.y }}
        >
          <button
            type="button"
            onClick={() => {
              void onAddWord?.(popover.text)
              setPopover(null)
            }}
            className="rounded-md px-2 py-1 text-[10px] font-medium hover:bg-white/10"
          >
            ➕ 加入生词本
          </button>
          <button
            type="button"
            onClick={() => {
              onAskAgent?.(popover.text)
              setPopover(null)
            }}
            className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-[10px] font-medium hover:bg-white/10"
          >
            <MessageSquarePlus className="h-3 w-3" /> 询问 Agent
          </button>
        </div>
      ) : null}

      <div className="flex items-center gap-1.5 px-1 text-[10px] text-slate-400">
        <Sparkles className="h-3 w-3 text-violet-500" />
        本页由 Agent 针对外源输入实时生成；划选单词可直接入库或追问。
      </div>
    </div>
  )
}
