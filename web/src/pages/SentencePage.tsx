import { useEffect, useRef, useState } from 'react'
import { Loader2 } from 'lucide-react'
import { AdHocSentenceCanvas } from '../components/AdHocSentenceCanvas'
import { SentenceLibraryDrawer } from '../components/SentenceLibraryDrawer'
import { useToast } from '../components/Toast'
import { useSearchParams } from 'react-router-dom'
import {
  api,
  type AdHocSentenceData,
  type SentenceBreakdown,
  type SentenceLibraryItem,
  type WorkspaceUnit,
} from '../lib/api'
import { useAppStore } from '../store/AppStore'
import { useSession } from '../store/SessionStore'
import { useWorkspace } from '../store/WorkspaceStore'

function breakdownToCanvas(
  sentenceId: string,
  sentenceEn: string,
  sourceLabel: string,
  breakdown: SentenceBreakdown,
  vocabulary: { word: string; basic_meaning: string; rare_meaning: string | null }[],
): AdHocSentenceData {
  return {
    sentence_en: sentenceEn,
    source_label: sourceLabel,
    word_count: breakdown.wordCount,
    step1_trunk: [breakdown.main, breakdown.mainNote].filter(Boolean).join('\n'),
    step2_clauses: (breakdown.clauses ?? []).map((item) => ({
      text: item.text,
      label: item.label,
      note: item.note,
    })),
    step3_modifiers: (breakdown.modifiers ?? []).map((item) => ({
      text: item.text,
      label: item.label,
      note: item.note,
    })),
    step4_translation: breakdown.translation,
    step4_translation_layers: breakdown.translationLayers,
    step5_vocab_and_grammar: {
      vocabulary: vocabulary.map((item) => ({
        word: item.word,
        meaning: item.basic_meaning,
        rare_meaning: item.rare_meaning,
      })),
      grammar: breakdown.grammar ?? [],
      exam_points: breakdown.examPoints ?? [],
    },
  }
}

export default function SentencePage() {
  const {
    workspaceUnit,
    openWorkspaceUnit,
    updateWorkspaceUnit,
    updateContext,
    setCanvasOp,
  } = useWorkspace()
  const { sendMessage } = useSession()
  const [searchParams] = useSearchParams()
  const { refresh } = useAppStore()
  const toast = useToast()
  const [libraryOpen, setLibraryOpen] = useState(false)
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>(
    workspaceUnit?.tier === 'sentence' ? 'ready' : 'loading',
  )
  const [markedWords, setMarkedWords] = useState<Set<string>>(new Set())
  const booted = useRef(false)
  const sentenceUnit = workspaceUnit?.tier === 'sentence' ? workspaceUnit : null
  const data = sentenceUnit?.data as AdHocSentenceData | undefined

  useEffect(() => {
    if (sentenceUnit) {
      setStatus('ready')
      updateContext({
        current_route: '/studio',
        active_passage_id: null,
        active_passage_label: sentenceUnit.label,
        active_question_id: null,
        active_sentence_id: sentenceUnit.id,
        selected_raw_text: data?.sentence_en ?? null,
      })
    }
  }, [data?.sentence_en, sentenceUnit, updateContext])

  useEffect(() => {
    if (sentenceUnit || booted.current) return
    booted.current = true
    let alive = true
    ;(async () => {
      try {
        const targetId = searchParams.get('sentence_id')
        if (targetId) {
          const [breakdown, workflow] = await Promise.all([
            api.getSentenceBreakdown(targetId),
            api.runSentence(targetId).catch(() => null),
          ])
          if (!alive) return
          openWorkspaceUnit({
            id: `exam-${targetId}`,
            tier: 'sentence',
            label: breakdown.source || '真题长难句',
            examSentenceId: targetId,
            data: breakdownToCanvas(
              targetId,
              breakdown.original,
              breakdown.source || '真题长难句',
              breakdown,
              workflow?.vocabulary ?? [],
            ),
            saved: false,
          })
          setStatus('ready')
          return
        }
        const library = await api.getSentenceLibrary()
        const first = library.featured[0]
        if (!first) {
          if (alive) setStatus('error')
          return
        }
        await loadFeatured(first)
      } catch {
        if (alive) setStatus('error')
      }
    })()
    return () => {
      alive = false
    }
    // bootstrap only when the workspace has no persisted unit
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function loadFeatured(item: SentenceLibraryItem) {
    setStatus('loading')
    const [breakdown, workflow] = await Promise.all([
      api.getSentenceBreakdown(item.id),
      api.runSentence(item.id).catch(() => null),
    ])
    const nextData = breakdownToCanvas(
      item.id,
      item.sentence_en,
      item.source_label || '真题精选长难句',
      breakdown,
      workflow?.vocabulary ?? [],
    )
    openWorkspaceUnit({
      id: `exam-${item.id}`,
      tier: 'sentence',
      label: item.source_label || '真题精选长难句',
      examSentenceId: item.id,
      data: nextData,
      saved: false,
    })
    setMarkedWords(new Set())
    setStatus('ready')
  }

  const selectFromLibrary = async (item: SentenceLibraryItem) => {
    setLibraryOpen(false)
    try {
      if (item.source_type === 'USER_SAVED') {
        const saved = await api.getSentenceAnalysis(item.id)
        openWorkspaceUnit({
          id: saved.id,
          tier: 'sentence',
          label: saved.source_label,
          examSentenceId: saved.exam_sentence_id,
          data: saved.data,
          saved: true,
        })
        setMarkedWords(new Set())
        setStatus('ready')
        return
      }
      await loadFeatured(item)
    } catch {
      toast('句子载入失败，请稍后重试。', 'error')
    }
  }

  const saveCurrent = async () => {
    if (!sentenceUnit || !data) return
    try {
      const result = await api.saveSentence({
        sentence_en: data.sentence_en,
        source_label: sentenceUnit.label,
        exam_sentence_id: sentenceUnit.examSentenceId ?? null,
        sentence_data: data,
      })
      updateWorkspaceUnit({
        id: result.analysis_id,
        label: result.source_label,
        saved: true,
      })
      toast('已存入长难句库。', 'success')
    } catch {
      toast('存入句库失败，请稍后重试。', 'error')
    }
  }

  const addWord = async (word: string) => {
    if (!sentenceUnit || !data) return
    try {
      const result = await api.addWordFromSentence({
        word,
        sentence_en: data.sentence_en,
        sentence_data: data,
        analysis_id: sentenceUnit.saved ? sentenceUnit.id : null,
        source_label: sentenceUnit.label,
      })
      if (!sentenceUnit.saved) {
        updateWorkspaceUnit({ id: result.analysis_id, saved: true })
      }
      setMarkedWords((prev) => new Set(prev).add(word.toLowerCase()))
      await refresh()
      toast(`已把 ${word} 连同原句语境加入词本。`, 'success')
    } catch {
      toast('加入词本失败，请稍后重试。', 'error')
    }
  }

  const askAboutWord = (word: string) => {
    updateContext({ selected_raw_text: word })
    setCanvasOp('push')
    void sendMessage(`请深度解析单词“${word}”，并结合当前句子说明它的熟词僻义与语法功能。`)
  }

  if (status === 'loading' && !sentenceUnit) {
    return (
      <div className="flex h-full min-h-[320px] items-center justify-center gap-2 text-sm text-slate-400">
        <Loader2 className="h-4 w-4 animate-spin" />
        正在载入长难句画布…
      </div>
    )
  }

  if (status === 'error' || !sentenceUnit || !data) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
        暂无长难句数据。可以直接让 Agent 拆解一句，或稍后重试。
      </div>
    )
  }

  const statusKind = sentenceUnit.saved
    ? 'saved'
    : sentenceUnit.examSentenceId
      ? 'featured'
      : 'draft'

  return (
    <>
      <SentenceLibraryDrawer
        open={libraryOpen}
        onClose={() => setLibraryOpen(false)}
        onSelect={(item) => void selectFromLibrary(item)}
      />
      <AdHocSentenceCanvas
        data={data}
        status={statusKind}
        onSave={() => void saveCurrent()}
        onOpenLibrary={() => setLibraryOpen(true)}
        onAddWord={(word) => addWord(word)}
        onAskAgent={askAboutWord}
        markedWords={markedWords}
      />
    </>
  )
}
