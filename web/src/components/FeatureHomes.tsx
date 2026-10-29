import { useEffect, useState, type ReactNode } from 'react'
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  FilePlus2,
  Headphones,
  Loader2,
  PenLine,
  Sparkles,
} from 'lucide-react'
import { api, type PassageSummary, type ReaderSource } from '../lib/api'
import { useSession } from '../store/SessionStore'
import { useWorkspace } from '../store/WorkspaceStore'
import { ContentLibraryDrawer } from './ContentLibraryDrawer'
import { useToast } from './Toast'

function splitSentences(text: string) {
  return text
    .split(/(?<=[.!?])\s+/)
    .map((item) => item.trim())
    .filter((item) => item.length >= 18)
    .slice(0, 10)
    .map((text, index) => ({ index: index + 1, text }))
}

function HomeShell({
  eyebrow,
  title,
  hint,
  children,
}: {
  eyebrow: string
  title: string
  hint: string
  children: ReactNode
}) {
  const { clearWorkspace } = useWorkspace()
  return (
    <div className="space-y-3">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <button
          type="button"
          onClick={() => clearWorkspace()}
          className="inline-flex items-center gap-1 text-[10px] text-slate-400 hover:text-slate-700"
        >
          <ArrowLeft className="h-3 w-3" /> Studio 首页
        </button>
        <p className="mt-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
          {eyebrow}
        </p>
        <h1 className="mt-1 text-xl font-bold tracking-tight text-slate-900">{title}</h1>
        <p className="mt-1 text-xs leading-6 text-slate-500">{hint}</p>
      </section>
      {children}
    </div>
  )
}

export function StudioHome() {
  const { openWorkspaceUnit } = useWorkspace()
  const { sendMessage } = useSession()
  const [sentence, setSentence] = useState('')

  const openHome = (feature: 'listening' | 'writing' | 'reader') => {
    const labels = {
      listening: '听力听写',
      writing: '写作批改',
      reader: '泛读文章',
    }
    openWorkspaceUnit({
      id: `home-${feature}`,
      tier: 'home',
      label: labels[feature],
      data: { feature },
    })
  }

  return (
    <div className="space-y-3">
      <section className="rounded-2xl bg-slate-900 px-5 py-5 text-white shadow-sm">
        <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-400">
          STUDIO · CHOOSE A MODE
        </p>
        <h1 className="mt-1 text-xl font-bold tracking-tight">今天想练哪一种？</h1>
        <p className="mt-1 text-xs text-slate-300">
          不再自动加载示例句。先选训练模式，再由你决定素材。
        </p>
      </section>

      <div className="grid gap-2 sm:grid-cols-2">
        <button type="button" onClick={() => openHome('listening')} className="group rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-50 text-violet-600"><Headphones className="h-4 w-4" /></span>
          <p className="mt-3 text-sm font-semibold text-slate-900">听力听写</p>
          <p className="mt-1 text-[10px] leading-5 text-slate-400">先选真题或粘贴文本，再逐句听写。</p>
          <span className="mt-2 inline-flex items-center gap-1 text-[10px] font-medium text-violet-600">进入听力首页 <ArrowRight className="h-3 w-3" /></span>
        </button>
        <button type="button" onClick={() => openHome('writing')} className="group rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-50 text-amber-600"><PenLine className="h-4 w-4" /></span>
          <p className="mt-3 text-sm font-semibold text-slate-900">写作批改</p>
          <p className="mt-1 text-[10px] leading-5 text-slate-400">先选题目或自由写作，再开始写。</p>
          <span className="mt-2 inline-flex items-center gap-1 text-[10px] font-medium text-amber-600">进入写作首页 <ArrowRight className="h-3 w-3" /></span>
        </button>
        <button type="button" onClick={() => openHome('reader')} className="group rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-50 text-cyan-600"><BookOpen className="h-4 w-4" /></span>
          <p className="mt-3 text-sm font-semibold text-slate-900">泛读文章</p>
          <p className="mt-1 text-[10px] leading-5 text-slate-400">从内容库选择已发布文章，点词查义。</p>
          <span className="mt-2 inline-flex items-center gap-1 text-[10px] font-medium text-cyan-600">进入泛读首页 <ArrowRight className="h-3 w-3" /></span>
        </button>
        <button type="button" onClick={() => window.location.assign('/vocab')} className="group rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600"><Sparkles className="h-4 w-4" /></span>
          <p className="mt-3 text-sm font-semibold text-slate-900">词汇记忆</p>
          <p className="mt-1 text-[10px] leading-5 text-slate-400">到期词、闪卡与四类词测。</p>
          <span className="mt-2 inline-flex items-center gap-1 text-[10px] font-medium text-emerald-600">进入记忆舱 <ArrowRight className="h-3 w-3" /></span>
        </button>
      </div>

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">长难句</p>
        <p className="mt-1 text-sm font-semibold text-slate-900">粘贴一句，再开始五步拆解</p>
        <div className="mt-2 flex gap-2">
          <input
            value={sentence}
            onChange={(event) => setSentence(event.target.value)}
            placeholder="Paste an English sentence…"
            className="h-9 flex-1 rounded-lg border border-slate-200 px-3 font-serif text-xs outline-none focus:border-slate-400"
          />
          <button
            type="button"
            disabled={sentence.trim().length < 8}
            onClick={() => void sendMessage(`请用五步法拆解这句：${sentence.trim()}`)}
            className="rounded-lg bg-slate-900 px-3 text-[11px] font-semibold text-white disabled:bg-slate-200"
          >
            开始拆解
          </button>
        </div>
      </section>
    </div>
  )
}

export function ListeningHome() {
  const { openWorkspaceUnit } = useWorkspace()
  const toast = useToast()
  const [passages, setPassages] = useState<PassageSummary[]>([])
  const [sources, setSources] = useState<ReaderSource[]>([])
  const [selected, setSelected] = useState<{ kind: 'passage' | 'source'; id: string } | null>(null)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.getPassages().then((response) => setPassages(response.items)).catch(() => {})
    api.getReaderSources('published').then((response) => setSources(response.items)).catch(() => {})
  }, [])

  const start = async () => {
    setLoading(true)
    try {
      let sourceText = text.trim()
      let label = '自定义听力 · 听写练习'
      if (!sourceText && selected?.kind === 'passage') {
        const response = await api.getPassageSentences(selected.id)
        sourceText = response.items.map((item) => item.text).join(' ')
        const passage = passages.find((item) => item.id === selected.id)
        label = passage ? `${passage.year} ${passage.exam_type} Text ${passage.text_number} · 听力听写` : label
      }
      if (!sourceText && selected?.kind === 'source') {
        const source = await api.getReaderSource(Number(selected.id))
        sourceText = source.text ?? ''
        label = `${source.title} · 泛读听力`
      }
      const sentences = splitSentences(sourceText)
      if (!sentences.length) {
        toast('这段文本没有可听写的完整句子，换一段或先粘贴英文。', 'error')
        return
      }
      openWorkspaceUnit({
        id: `listening-${Date.now()}`,
        tier: 'listening',
        label,
        data: { source_label: label, sentences },
      })
    } catch {
      toast('素材加载失败。', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <HomeShell eyebrow="LISTENING HOME" title="先选素材，再开始听写" hint="不再自动塞一篇默认文章。选一篇已发布真题、内容库文章，或粘贴自己的英文。">
      <div className="grid gap-3 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">已发布真题</p>
          <div className="mt-2 max-h-64 space-y-1 overflow-y-auto">
            {passages.map((passage) => {
              const active = selected?.kind === 'passage' && selected.id === passage.id
              return (
                <button
                  key={passage.id}
                  type="button"
                  onClick={() => { setSelected({ kind: 'passage', id: passage.id }); setText('') }}
                  className={`w-full rounded-lg border px-3 py-2 text-left text-[11px] ${active ? 'border-violet-300 bg-violet-50 text-violet-800' : 'border-slate-100 text-slate-600 hover:bg-slate-50'}`}
                >
                  {passage.year} {passage.exam_type} · Text {passage.text_number}
                  <span className="ml-1 text-[9px] text-slate-400">{passage.sentence_count} 句</span>
                </button>
              )
            })}
            {!passages.length ? <p className="py-4 text-center text-[10px] text-slate-400">暂无已发布真题。</p> : null}
          </div>
          {sources.length ? (
            <>
              <p className="mt-4 text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">内容库</p>
              <div className="mt-2 max-h-40 space-y-1 overflow-y-auto">
                {sources.map((source) => {
                  const active = selected?.kind === 'source' && selected.id === String(source.id)
                  return (
                    <button
                      key={source.id}
                      type="button"
                      onClick={() => { setSelected({ kind: 'source', id: String(source.id) }); setText('') }}
                      className={`w-full rounded-lg border px-3 py-2 text-left text-[11px] ${active ? 'border-violet-300 bg-violet-50 text-violet-800' : 'border-slate-100 text-slate-600 hover:bg-slate-50'}`}
                    >
                      {source.title}
                    </button>
                  )
                })}
              </div>
            </>
          ) : null}
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">或粘贴一段英文</p>
          <textarea
            value={text}
            onChange={(event) => { setText(event.target.value); setSelected(null) }}
            rows={7}
            placeholder="Paste an English article or paragraph…"
            className="mt-2 w-full resize-y rounded-lg border border-slate-200 p-3 font-serif text-xs leading-6 outline-none focus:border-slate-400"
          />
          <button
            type="button"
            onClick={() => void start()}
            disabled={loading || (!text.trim() && !selected)}
            className="mt-2 inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3.5 py-2 text-[11px] font-semibold text-white disabled:bg-slate-200"
          >
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Headphones className="h-3.5 w-3.5" />}
            开始听写
          </button>
        </section>
      </div>
    </HomeShell>
  )
}

const WRITING_PROMPTS = [
  { title: 'AI 与学习', prompt: 'Write an essay on whether AI should be used in students’ daily learning. Give your opinion and support it with reasons.' },
  { title: '绿色生活', prompt: 'Write an essay suggesting how university students can adopt a greener lifestyle. Give specific examples.' },
  { title: '一封建议信', prompt: 'Write a letter to your university suggesting one improvement to the library and explain why it matters.' },
]

export function WritingHome() {
  const { openWorkspaceUnit } = useWorkspace()
  const [custom, setCustom] = useState('')

  const open = (prompt: string) => {
    openWorkspaceUnit({
      id: `writing-${Date.now()}`,
      tier: 'writing',
      label: '写作批改',
      data: { source_label: '考研英语写作 · 最小修改', prompt, draft: '' },
    })
  }

  return (
    <HomeShell eyebrow="WRITING HOME" title="先选题目，再开始写" hint="不再直接打开空白作文。选一个题目，或输入你自己的题目。">
      <div className="grid gap-2 sm:grid-cols-3">
        {WRITING_PROMPTS.map((item) => (
          <button key={item.title} type="button" onClick={() => open(item.prompt)} className="rounded-2xl border border-slate-200 bg-white p-4 text-left shadow-sm hover:-translate-y-0.5 hover:shadow-md">
            <PenLine className="h-4 w-4 text-amber-500" />
            <p className="mt-3 text-sm font-semibold text-slate-900">{item.title}</p>
            <p className="mt-1 line-clamp-3 text-[10px] leading-5 text-slate-400">{item.prompt}</p>
          </button>
        ))}
      </div>
      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">自定义题目</p>
        <div className="mt-2 flex gap-2">
          <input value={custom} onChange={(event) => setCustom(event.target.value)} placeholder="输入作文题目…" className="h-9 flex-1 rounded-lg border border-slate-200 px-3 text-xs outline-none focus:border-slate-400" />
          <button type="button" disabled={custom.trim().length < 5} onClick={() => open(custom.trim())} className="rounded-lg bg-slate-900 px-3 text-[11px] font-semibold text-white disabled:bg-slate-200">开始写作</button>
        </div>
      </section>
    </HomeShell>
  )
}

export function ReaderHome() {
  const { openWorkspaceUnit } = useWorkspace()
  const toast = useToast()
  const [sources, setSources] = useState<ReaderSource[]>([])
  const [libraryOpen, setLibraryOpen] = useState(false)
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    api.getReaderSources('published').then((response) => setSources(response.items)).catch(() => setSources([])).finally(() => setLoading(false))
  }
  useEffect(() => { load() }, [])

  const open = async (id: number) => {
    try {
      const source = await api.getReaderSource(id)
      openWorkspaceUnit({
        id: `reader-${source.id}`,
        tier: 'reader',
        label: source.title,
        data: {
          title: source.title,
          text: source.text ?? '',
          source_label: source.license ? `泛读 · ${source.license}` : '内容库泛读',
          source_url: source.source_url,
          license: source.license,
          source_id: source.id,
        },
      })
    } catch {
      toast('文章打开失败。', 'error')
    }
  }

  return (
    <HomeShell eyebrow="READING HOME" title="选一篇你真正想读的" hint="不再自动打开默认文章。从已发布内容库里选，或先导入自己的文章。">
      <div className="flex items-center justify-between">
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-400">已发布文章</p>
        <button type="button" onClick={() => setLibraryOpen(true)} className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-[10px] font-medium text-slate-600 hover:bg-slate-50"><FilePlus2 className="h-3 w-3" /> 导入 / 管理内容</button>
      </div>
      {loading ? <div className="py-8 text-center text-xs text-slate-400">加载中…</div> : sources.length ? (
        <div className="grid gap-2 sm:grid-cols-2">
          {sources.map((source) => (
            <button key={source.id} type="button" onClick={() => void open(source.id)} className="rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm hover:-translate-y-0.5 hover:shadow-md">
              <p className="text-sm font-semibold text-slate-900">{source.title}</p>
              <p className="mt-1 text-[10px] text-slate-400">{source.word_count} words · {source.license || '未标注许可'}</p>
              <p className="mt-2 line-clamp-2 text-[10px] leading-5 text-slate-500">{source.preview}</p>
            </button>
          ))}
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-slate-200 bg-white p-10 text-center">
          <p className="text-sm font-semibold text-slate-800">还没有已发布文章</p>
          <p className="mt-1 text-xs text-slate-400">先导入一篇你有权使用的文章，确认许可后发布。</p>
          <button type="button" onClick={() => setLibraryOpen(true)} className="mt-3 rounded-lg bg-slate-900 px-3 py-2 text-[11px] font-semibold text-white">打开内容库</button>
        </div>
      )}
      <ContentLibraryDrawer open={libraryOpen} onClose={() => { setLibraryOpen(false); load() }} />
    </HomeShell>
  )
}
