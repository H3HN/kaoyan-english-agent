import { useState, type FormEvent } from 'react'
import { Loader2, Plus, X } from 'lucide-react'
import { Tag } from './Tag'
import { useToast } from './Toast'
import { api, type FullQuestion } from '../lib/api'

interface ExamImportFormProps {
  onClose: () => void
  onImported: (question: FullQuestion) => void
  onBatchImported: (questions: FullQuestion[]) => void
}

type Mode = 'auto' | 'manual'

const fieldClass =
  'mt-1.5 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs text-slate-800 outline-none transition-colors placeholder:text-slate-300 focus:border-blue-400 focus:ring-2 focus:ring-blue-500/10'
const labelClass = 'text-[11px] font-medium text-slate-500'

export function ExamImportForm({
  onClose,
  onImported,
  onBatchImported,
}: ExamImportFormProps) {
  const [mode, setMode] = useState<Mode>('auto')
  const [loading, setLoading] = useState(false)
  const [autoForm, setAutoForm] = useState({
    url: '',
    year: String(new Date().getFullYear()),
    examType: '英语一',
    textNumber: '1',
    answerKey: '',
  })
  const [form, setForm] = useState({
    year: String(new Date().getFullYear()),
    examType: '英语一',
    textNumber: '1',
    passage: '',
    questionType: '细节题',
    content: '',
    options: { A: '', B: '', C: '', D: '' },
    correctAnswer: 'B',
  })
  const toast = useToast()

  const updateOption = (key: 'A' | 'B' | 'C' | 'D', value: string) => {
    setForm((prev) => ({
      ...prev,
      options: { ...prev.options, [key]: value },
    }))
  }

  const handleAutoSubmit = async () => {
    if (!/^https?:\/\//i.test(autoForm.url.trim())) {
      toast('请填写 PDF 的 http(s) 地址。', 'error')
      return
    }
    setLoading(true)
    try {
      const response = await api.autoImportExam({
        url: autoForm.url.trim(),
        year: Number(autoForm.year),
        exam_type: autoForm.examType,
        text_number: Number(autoForm.textNumber),
        answer_key: autoForm.answerKey.trim(),
      })
      const count = response.questions.length
      toast(
        response.answer_source === 'inferred'
          ? `已导入 ${count} 题；答案为 AI 推断，请核对。`
          : `已导入 ${count} 题。`,
        response.answer_source === 'inferred' ? 'info' : 'success',
      )
      onBatchImported(response.questions)
      onClose()
    } catch {
      toast('自动解析失败，请检查 PDF 地址或稍后重试。', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleManualSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (form.passage.trim().length < 50) {
      toast('文章太短，至少粘贴 50 个字符。', 'error')
      return
    }
    if (!form.content.trim()) {
      toast('请填写题干。', 'error')
      return
    }
    if (Object.values(form.options).some((value) => !value.trim())) {
      toast('A/B/C/D 四个选项都需要填写。', 'error')
      return
    }

    setLoading(true)
    try {
      const response = await api.importExam({
        year: Number(form.year),
        exam_type: form.examType,
        text_number: Number(form.textNumber),
        passage: form.passage.trim(),
        question_type: form.questionType,
        content: form.content.trim(),
        options: form.options,
        correct_answer: form.correctAnswer,
      })
      toast(
        response.analysis_source === 'deepseek'
          ? '真题已导入，DeepSeek 已完成四个选项分析。'
          : '真题已导入；选项分析使用占位结果。',
        response.analysis_source === 'deepseek' ? 'success' : 'info',
      )
      onImported(response.question)
      onClose()
    } catch {
      toast('导入失败，请检查后端服务和文章格式。', 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        if (mode === 'auto') void handleAutoSubmit()
        else void handleManualSubmit(event)
      }}
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold text-slate-900">添加真题</h2>
          <Tag tone="violet">DeepSeek</Tag>
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="关闭导入"
          className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-700"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="mt-3 inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1">
        {(
          [
            { id: 'auto', label: 'PDF 自动导入' },
            { id: 'manual', label: '手动录入' },
          ] as const
        ).map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setMode(item.id)}
            className={`rounded-md px-3 py-1.5 text-[11px] font-medium transition-colors ${
              mode === item.id
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-500 hover:text-slate-800'
            }`}
            aria-pressed={mode === item.id}
          >
            {item.label}
          </button>
        ))}
      </div>

      {mode === 'auto' ? (
        <>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <label className={`${labelClass} sm:col-span-2`}>
              PDF 地址
              <input
                value={autoForm.url}
                onChange={(event) =>
                  setAutoForm((prev) => ({ ...prev, url: event.target.value }))
                }
                placeholder="https://...pdf"
                className={fieldClass}
              />
            </label>
            <label className={labelClass}>
              年份
              <input
                value={autoForm.year}
                onChange={(event) =>
                  setAutoForm((prev) => ({ ...prev, year: event.target.value }))
                }
                inputMode="numeric"
                className={fieldClass}
              />
            </label>
            <label className={labelClass}>
              试卷
              <select
                value={autoForm.examType}
                onChange={(event) =>
                  setAutoForm((prev) => ({
                    ...prev,
                    examType: event.target.value,
                  }))
                }
                className={fieldClass}
              >
                <option>英语一</option>
                <option>英语二</option>
              </select>
            </label>
            <label className={labelClass}>
              Text
              <input
                value={autoForm.textNumber}
                onChange={(event) =>
                  setAutoForm((prev) => ({
                    ...prev,
                    textNumber: event.target.value,
                  }))
                }
                inputMode="numeric"
                className={fieldClass}
              />
            </label>
            <label className={labelClass}>
              答案序列
              <input
                value={autoForm.answerKey}
                onChange={(event) =>
                  setAutoForm((prev) => ({
                    ...prev,
                    answerKey: event.target.value,
                  }))
                }
                placeholder="如 21-25 BCDAB（可选）"
                className={fieldClass}
              />
            </label>
          </div>

          <div className="mt-4 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-200 px-4 py-2.5 text-xs font-medium text-slate-500 transition-colors hover:bg-slate-50"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2.5 text-xs font-semibold text-white transition-colors hover:bg-slate-900 disabled:bg-slate-300"
            >
              {loading ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Plus className="h-3.5 w-3.5" />
              )}
              {loading ? '解析中…' : '下载并解析'}
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <label className={labelClass}>
              年份
              <input
                value={form.year}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, year: event.target.value }))
                }
                inputMode="numeric"
                className={fieldClass}
              />
            </label>
            <label className={labelClass}>
              试卷
              <select
                value={form.examType}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, examType: event.target.value }))
                }
                className={fieldClass}
              >
                <option>英语一</option>
                <option>英语二</option>
              </select>
            </label>
            <label className={labelClass}>
              Text
              <input
                value={form.textNumber}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    textNumber: event.target.value,
                  }))
                }
                inputMode="numeric"
                className={fieldClass}
              />
            </label>
          </div>

          <label className={`mt-3 block ${labelClass}`}>
            文章
            <textarea
              value={form.passage}
              onChange={(event) =>
                setForm((prev) => ({ ...prev, passage: event.target.value }))
              }
              rows={4}
              placeholder="Paste the reading passage..."
              className={`${fieldClass} resize-y font-serif leading-7`}
            />
          </label>

          <div className="mt-3 grid gap-3 sm:grid-cols-[160px_minmax(0,1fr)]">
            <label className={labelClass}>
              题型
              <select
                value={form.questionType}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    questionType: event.target.value,
                  }))
                }
                className={fieldClass}
              >
                <option>细节题</option>
                <option>主旨题</option>
                <option>推理题</option>
                <option>词义题</option>
                <option>态度题</option>
              </select>
            </label>
            <label className={labelClass}>
              题干
              <input
                value={form.content}
                onChange={(event) =>
                  setForm((prev) => ({ ...prev, content: event.target.value }))
                }
                placeholder="What is the main idea of the passage?"
                className={fieldClass}
              />
            </label>
          </div>

          <div className="mt-3 grid gap-3 sm:grid-cols-2">
            {(['A', 'B', 'C', 'D'] as const).map((key) => (
              <label key={key} className={labelClass}>
                选项 {key}
                <input
                  value={form.options[key]}
                  onChange={(event) => updateOption(key, event.target.value)}
                  className={fieldClass}
                />
              </label>
            ))}
          </div>

          <div className="mt-3 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <label className={`w-full sm:w-[160px] ${labelClass}`}>
              正确答案
              <select
                value={form.correctAnswer}
                onChange={(event) =>
                  setForm((prev) => ({
                    ...prev,
                    correctAnswer: event.target.value,
                  }))
                }
                className={fieldClass}
              >
                {['A', 'B', 'C', 'D'].map((key) => (
                  <option key={key}>{key}</option>
                ))}
              </select>
            </label>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="rounded-lg border border-slate-200 px-4 py-2.5 text-xs font-medium text-slate-500 transition-colors hover:bg-slate-50"
              >
                取消
              </button>
              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-lg bg-slate-800 px-4 py-2.5 text-xs font-semibold text-white transition-colors hover:bg-slate-900 disabled:bg-slate-300"
              >
                {loading ? (
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                ) : (
                  <Plus className="h-3.5 w-3.5" />
                )}
                {loading ? '分析中…' : '导入并分析'}
              </button>
            </div>
          </div>
        </>
      )}
    </form>
  )
}
