import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import type { ClientAction, WorkspaceUnit } from './api'
import { useWorkspace } from '../store/WorkspaceStore'
import { useUI } from '../store/UIStore'
import { useAppStore } from '../store/AppStore'

export function useAgentActions() {
  const navigate = useNavigate()
  const {
    workspaceUnit,
    openWorkspaceUnit,
    updateWorkspaceUnit,
    updateContext,
    canvasOp,
    setCanvasOp,
  } = useWorkspace()
  const { setFlashcardOpen } = useUI()
  const { refresh } = useAppStore()

  return useCallback(
    (action: ClientAction) => {
      const payload = action.payload ?? {}
      if (action.action_type === 'APPLY_CANVAS_COMMAND') {
        const unit = payload.unit as WorkspaceUnit | undefined
        if (unit?.tier) {
          const op = payload.op === 'push' ? 'push' : canvasOp
          openWorkspaceUnit(unit, op)
          setCanvasOp('replace')
          updateContext({
            current_route: '/studio',
            active_passage_id: null,
            active_passage_label: unit.label,
            active_question_id: null,
            active_sentence_id: unit.tier === 'sentence' ? unit.id : null,
            selected_raw_text: null,
          })
        }
        navigate('/studio')
        return
      }
      if (action.action_type === 'NAVIGATE_TO') {
        const route = String(payload.route ?? '/')
        const params = new URLSearchParams()
        for (const key of [
          'year',
          'exam_type',
          'text_number',
          'question_id',
          'sentence_id',
          'passage_id',
        ]) {
          if (payload[key] !== undefined && payload[key] !== null) {
            params.set(key, String(payload[key]))
          }
        }
        navigate(params.toString() ? `${route}?${params.toString()}` : route)
        return
      }
      if (action.action_type === 'SAVE_SENTENCE_STATE') {
        updateWorkspaceUnit({
          id: String(payload.analysis_id ?? workspaceUnit?.id ?? ''),
          saved: true,
          label: String(payload.source_label ?? workspaceUnit?.label ?? '单句精析'),
        })
        updateContext({
          active_passage_label: String(payload.source_label ?? workspaceUnit?.label ?? '单句精析'),
        })
        return
      }
      if (action.action_type === 'HIGHLIGHT_SENTENCE' || action.action_type === 'REVEAL_OPTION_ANALYSIS') {
        const questionId = payload.question_id
        if (questionId) {
          const params = new URLSearchParams({
            question_id: String(questionId),
            reveal: '1',
          })
          if (action.action_type === 'HIGHLIGHT_SENTENCE') params.set('highlight', '1')
          navigate(`/reading?${params.toString()}`)
        }
        return
      }
      if (action.action_type === 'OPEN_FLASHCARD_DRAWER') {
        setFlashcardOpen(true)
        return
      }
      if (action.action_type === 'WORD_ADDED' || action.action_type === 'REFRESH_QUERY') {
        void refresh()
      }
    },
    [
      navigate,
      openWorkspaceUnit,
      refresh,
      setFlashcardOpen,
      updateContext,
      canvasOp,
      setCanvasOp,
      updateWorkspaceUnit,
      workspaceUnit,
    ],
  )
}
