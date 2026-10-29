import { useEffect } from 'react'
import { ChevronRight, Layers } from 'lucide-react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { AdHocReadingCanvas } from '../components/AdHocReadingCanvas'
import { AdHocVocabCanvas } from '../components/AdHocVocabCanvas'
import { ListeningCanvas } from '../components/ListeningCanvas'
import { ParagraphCanvas } from '../components/ParagraphCanvas'
import { PlanCanvas } from '../components/PlanCanvas'
import { ReaderCanvas } from '../components/ReaderCanvas'
import { ListeningHome, ReaderHome, StudioHome, WritingHome } from '../components/FeatureHomes'
import { WordInsightCanvas } from '../components/WordInsightCanvas'
import { WritingCanvas } from '../components/WritingCanvas'
import SentencePage from './SentencePage'
import { useSession } from '../store/SessionStore'
import { useWorkspace } from '../store/WorkspaceStore'
import type {
  AdHocReadingData,
  AdHocSentenceData,
  AdHocVocabData,
  ListeningData,
  ParagraphData,
  ReaderData,
  ScheduleTask,
  WordInsightData,
  WritingData,
} from '../lib/api'

export default function StudioPage() {
  const {
    workspaceUnit,
    workspaceStack,
    popWorkspaceTo,
    clearWorkspace,
    setCanvasOp,
    updateContext,
    openWorkspaceUnit,
  } = useWorkspace()
  const { sendMessage } = useSession()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  useEffect(() => {
    if (!workspaceUnit) return
    updateContext({
      current_route: '/studio',
      active_passage_id: null,
      active_passage_label: workspaceUnit.label,
      active_question_id: null,
      active_sentence_id:
        workspaceUnit.tier === 'sentence' ? workspaceUnit.id : null,
      selected_raw_text: null,
    })
  }, [updateContext, workspaceUnit])

  const drill = (text: string) => {
    setCanvasOp('push')
    void sendMessage(`请用五步法拆解这句：${text}`)
  }

  const breadcrumbs = workspaceStack.map((unit, index) => ({
    ...unit,
    index,
    short:
      unit.tier === 'word' || unit.tier === 'phrase'
        ? `🔤 ${unit.label}`
        : unit.tier === 'home'
          ? `🏠 ${unit.label}`
          : unit.tier === 'paragraph'
            ? '📑 段落精读'
          : unit.tier === 'plan'
            ? '📅 学习计划'
            : unit.tier === 'vocab'
              ? '🃏 生词视图'
              : unit.tier === 'reading'
                ? '📖 阅读验伪'
                : unit.tier === 'listening'
                  ? '🎧 听力听写'
                  : unit.tier === 'writing'
                    ? '✍️ 写作批改'
                    : unit.tier === 'reader'
                      ? '📰 泛读器'
                      : '🧬 单句拆解',
  }))

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-2.5 py-2">
        <span className="mr-1 text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-400">训练入口</span>
        <button
          type="button"
          onClick={() => openWorkspaceUnit({ id: 'home-listening', tier: 'home', label: '听力听写', data: { feature: 'listening' } })}
          className="rounded-md border border-slate-200 px-2.5 py-1 text-[10px] font-medium text-slate-600 hover:bg-slate-50"
        >
          🎧 听力
        </button>
        <button
          type="button"
          onClick={() => openWorkspaceUnit({ id: 'home-writing', tier: 'home', label: '写作批改', data: { feature: 'writing' } })}
          className="rounded-md border border-slate-200 px-2.5 py-1 text-[10px] font-medium text-slate-600 hover:bg-slate-50"
        >
          ✍️ 写作
        </button>
        <button
          type="button"
          onClick={() => openWorkspaceUnit({ id: 'home-reader', tier: 'home', label: '泛读文章', data: { feature: 'reader' } })}
          className="rounded-md border border-slate-200 px-2.5 py-1 text-[10px] font-medium text-slate-600 hover:bg-slate-50"
        >
          📰 泛读
        </button>
        <button
          type="button"
          onClick={() => navigate('/vocab?tab=quiz')}
          className="rounded-md border border-slate-200 px-2.5 py-1 text-[10px] font-medium text-slate-600 hover:bg-slate-50"
        >
          🧠 词测
        </button>
      </div>

      {breadcrumbs.length ? (
        <nav className="flex flex-wrap items-center gap-1 rounded-xl border border-slate-200 bg-white px-3 py-2 text-[10px] text-slate-500">
          <button
            type="button"
            onClick={() => clearWorkspace()}
            className="flex items-center gap-1 rounded px-1 py-0.5 font-medium text-slate-700 hover:bg-slate-50"
          >
            <Layers className="h-3 w-3" /> Studio
          </button>
          {breadcrumbs.map((crumb) => (
            <span key={crumb.id} className="flex items-center gap-1">
              <ChevronRight className="h-3 w-3 text-slate-300" />
              <button
                type="button"
                onClick={() => popWorkspaceTo(crumb.index)}
                className={`max-w-[220px] truncate rounded px-1 py-0.5 hover:bg-slate-50 ${
                  crumb.index === breadcrumbs.length - 1
                    ? 'font-semibold text-slate-800'
                    : 'text-slate-500'
                }`}
              >
                {crumb.short}
              </button>
            </span>
          ))}
        </nav>
      ) : null}

      {!workspaceUnit && !searchParams.get('sentence_id') ? <StudioHome /> : null}

      {!workspaceUnit && searchParams.get('sentence_id') ? <SentencePage /> : null}

      {workspaceUnit?.tier === 'sentence' ? <SentencePage /> : null}

      {workspaceUnit?.tier === 'home' ? (
        (workspaceUnit.data as { feature?: string }).feature === 'listening' ? <ListeningHome />
          : (workspaceUnit.data as { feature?: string }).feature === 'writing' ? <WritingHome />
            : (workspaceUnit.data as { feature?: string }).feature === 'reader' ? <ReaderHome />
              : <StudioHome />
      ) : null}

      {workspaceUnit?.tier === 'word' || workspaceUnit?.tier === 'phrase' ? (
        <WordInsightCanvas
          data={workspaceUnit.data as WordInsightData}
          onDrillSentence={drill}
        />
      ) : null}

      {workspaceUnit?.tier === 'paragraph' ? (
        <ParagraphCanvas
          data={workspaceUnit.data as ParagraphData}
          onDrillSentence={drill}
          onHarvest={() => {
            const data = workspaceUnit.data as ParagraphData
            setCanvasOp('push')
            void sendMessage(`把这段里的生词整理入库：${data.paragraph_en}`)
          }}
          onQuiz={() => {
            const data = workspaceUnit.data as ParagraphData
            void sendMessage(`用这段话生成 2 道考研仿真阅读题：${data.paragraph_en}`)
          }}
        />
      ) : null}

      {workspaceUnit?.tier === 'plan' ? (
        <PlanCanvas
          data={workspaceUnit.data as { source_label?: string; tasks: ScheduleTask[] }}
        />
      ) : null}

      {workspaceUnit?.tier === 'vocab' ? (
        <AdHocVocabCanvas
          data={workspaceUnit.data as AdHocVocabData}
          onClose={() => {
            if (workspaceStack.length > 1) popWorkspaceTo(workspaceStack.length - 2)
            else clearWorkspace()
          }}
        />
      ) : null}

      {workspaceUnit?.tier === 'reader' ? (
        <ReaderCanvas data={workspaceUnit.data as ReaderData} />
      ) : null}

      {workspaceUnit?.tier === 'listening' ? (
        <ListeningCanvas data={workspaceUnit.data as ListeningData} />
      ) : null}

      {workspaceUnit?.tier === 'writing' ? (
        <WritingCanvas data={workspaceUnit.data as WritingData} />
      ) : null}

      {workspaceUnit?.tier === 'reading' ? (
        <AdHocReadingCanvas
          data={workspaceUnit.data as AdHocReadingData}
          onClose={() => {
            if (workspaceStack.length > 1) popWorkspaceTo(workspaceStack.length - 2)
            else clearWorkspace()
          }}
        />
      ) : null}

      {workspaceUnit?.tier === 'sentence' ? (
        <span className="sr-only">
          {(workspaceUnit.data as AdHocSentenceData).sentence_en}
        </span>
      ) : null}
    </div>
  )
}
