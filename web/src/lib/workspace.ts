import type { SavedSentenceAnalysis, WorkspaceUnit } from './api'

export function unitFromSavedSentence(saved: SavedSentenceAnalysis): WorkspaceUnit {
  return {
    id: saved.id,
    tier: 'sentence',
    label: saved.source_label,
    examSentenceId: saved.exam_sentence_id,
    data: saved.data,
    saved: true,
  }
}
