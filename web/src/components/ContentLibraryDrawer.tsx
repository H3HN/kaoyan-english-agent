import { useEffect, useState } from 'react'
import { ArrowUpRight, BookOpen, CheckCircle2, FilePlus2, Loader2, Upload, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { api, type ReaderSource } from '../lib/api'
import { useWorkspace } from '../store/WorkspaceStore'
import { useToast } from './Toast'
import { Tag } from './Tag'

export function ContentLibraryDrawer({
  open,
  onClose,
}: {
  open: boolean
  onClose: () => void
}) {
  const navigate = useNavigate()
  const { openWorkspaceUnit } = useWorkspace()
  const toast = useToast()
  const [sources, setSources] = useState<ReaderSource[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({ title: '', text: '', source_url: '', license: '' })

  const load = () => {
    setLoading(true)
    api
      .getReaderSources()
      .then((response) => setSources(response.items))
      .catch(() => setSources([]))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (open) load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  if (!open) return null

  const importArticle = async () => {
    if (form.text.trim().length < 200) {
      toast('文章至少需要 200 个字符，避免把碎片文本当泛读。', 'error')
      return
    }
    setSaving(true)
    try {
      const response = await api.importReaderSource(form)
      setSources((prev) => [response.source, ...prev])
      setForm({ title: '', text: '', source_url: '', license: '' })
      toast('已存为 draft。确认来源与许可后再发布。', 'success')
    } catch {
      toast('导入失败，请检查后端或文本长度。', 'error')
    } finally {
      setSaving(false)
    }
  }

  const publish = async (id: number) => {
    try {
      const response = await api.publishReaderSource(id)
      setSources((prev) => prev.map((item) => (item.id === id ? response.source : item)))
      toast('文章已发布，可进入泛读器。', 'success')
    } catch {
      toast('发布失败，请稍后重试。', 'error')
    }
  }

  const read = async (id: number) => {
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
      onClose()
      navigate('/studio')
    } catch {
      toast('文章打开失败。', 'error')
    }
  }

  return (
    <div className="fixed inset-0 z-[80] flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-[2px]">
      <div className="flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-2xl">
        <div className="flex items-start justify-between gap-3 border-b border-slate-100 px-5 py-4">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">CONTENT PIPELINE</p>
            <h2 className="mt-1 text-lg font-bold text-slate-900">泛读内容库</h2>
            <p className="mt-1 text-[10px] text-slate-400">先导入 draft，确认来源与许可，再发布到泛读器。</p>
          </div>
          <button type="button" onClick={onClose} aria-label="关闭内容库" className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100"><X className="h-4 w-4" /></button>
        </div>

        <div className="grid min-h-0 flex-1 gap-0 overflow-y-auto md:grid-cols-[0.9fr_1.1fr]">
          <section className="border-b border-slate-100 p-4 md:border-b-0 md:border-r">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
              <FilePlus2 className="h-4 w-4 text-violet-500" /> 导入一篇文章
            </div>
            <p className="mt-1 text-[10px] leading-5 text-slate-400">只接收你有权使用的文本。来源和许可会随文章保存。</p>
            <div className="mt-3 space-y-2">
              <input value={form.title} onChange={(event) => setForm((prev) => ({ ...prev, title: event.target.value }))} placeholder="标题" className="h-9 w-full rounded-lg border border-slate-200 px-3 text-xs outline-none focus:border-slate-400" />
              <div className="grid grid-cols-2 gap-2">
                <input value={form.source_url} onChange={(event) => setForm((prev) => ({ ...prev, source_url: event.target.value }))} placeholder="来源 URL（可选）" className="h-9 w-full rounded-lg border border-slate-200 px-3 text-[10px] outline-none focus:border-slate-400" />
                <input value={form.license} onChange={(event) => setForm((prev) => ({ ...prev, license: event.target.value }))} placeholder="许可 / 来源说明" className="h-9 w-full rounded-lg border border-slate-200 px-3 text-[10px] outline-none focus:border-slate-400" />
              </div>
              <textarea value={form.text} onChange={(event) => setForm((prev) => ({ ...prev, text: event.target.value }))} rows={11} placeholder="粘贴文章正文，至少 200 字符…" className="w-full resize-y rounded-lg border border-slate-200 p-3 font-serif text-[12px] leading-6 outline-none focus:border-slate-400" />
              <button type="button" onClick={() => void importArticle()} disabled={saving} className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3 py-2 text-[11px] font-semibold text-white disabled:bg-slate-200">
                {saving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Upload className="h-3.5 w-3.5" />}
                {saving ? '导入中…' : '存为 draft'}
              </button>
            </div>
          </section>

          <section className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
                <BookOpen className="h-4 w-4 text-cyan-600" /> 内容列表
              </div>
              <span className="text-[10px] text-slate-400">{sources.length} 篇</span>
            </div>
            {loading ? (
              <div className="py-10 text-center text-xs text-slate-400">加载中…</div>
            ) : sources.length ? (
              <div className="mt-2 space-y-2">
                {sources.map((source) => (
                  <div key={source.id} className="rounded-xl border border-slate-200 p-3">
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="truncate text-xs font-semibold text-slate-800">{source.title}</p>
                        <p className="mt-0.5 text-[9px] text-slate-400">{source.word_count} words · {source.license || '未标注许可'}</p>
                      </div>
                      <Tag tone={source.status === 'published' ? 'emerald' : 'slate'}>{source.status === 'published' ? '已发布' : 'draft'}</Tag>
                    </div>
                    <p className="mt-1 line-clamp-2 text-[10px] leading-5 text-slate-500">{source.preview}</p>
                    <div className="mt-2 flex gap-2">
                      {source.status === 'draft' ? (
                        <button type="button" onClick={() => void publish(source.id)} className="inline-flex items-center gap-1 rounded-md bg-slate-900 px-2.5 py-1.5 text-[10px] font-semibold text-white"><CheckCircle2 className="h-3 w-3" /> 发布</button>
                      ) : (
                        <button type="button" onClick={() => void read(source.id)} className="inline-flex items-center gap-1 rounded-md bg-cyan-600 px-2.5 py-1.5 text-[10px] font-semibold text-white"><ArrowUpRight className="h-3 w-3" /> 泛读</button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="mt-6 rounded-xl border border-dashed border-slate-200 p-8 text-center text-xs text-slate-400">还没有内容。先导入一篇你有权使用的文章。</div>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}
