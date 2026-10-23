import type { StudyRecord, Word } from '../types'

const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? '/api'

export interface ToolCall {
  tool: string
  args?: Record<string, unknown>
  summary: string
  duration_ms: number
}

export interface Citation {
  id: string
  source: string
  year: number
  exam_type: string
  text: string
  grammar_tags: string[]
}

export interface VocabEntry {
  word: string
  matched: string | null
  in_syllabus: boolean
  level: string
  basic_meaning: string
  rare_meaning: string | null
  exam_frequency: number
  source: string
}

export interface SentenceWorkflow {
  sentence: {
    id: string
    passage_id: string
    year: number
    exam_type: string
    text_number: number
    paragraph: number
    sentence_index: number
    text: string
    grammar_tags: string[]
    source: string
  }
  vocabulary: VocabEntry[]
  vocabulary_all_count: number
  citations: Citation[]
  tool_trace: ToolCall[]
}

export interface OptionWorkflow {
  question: {
    id: string
    year: number
    exam_type: string
    text_number: number
    number: number
    question_type: string
    content: string
    options: Record<string, string>
    correct_answer: string
    analysis: Record<string, { trapType: string; explanation: string }>
    steps: string[]
    source_sentence_id: string
  }
  source_sentence: {
    id: string
    text: string
    source: string
    grammar_tags: string[]
  } | null
  citations: Citation[]
  is_correct: boolean | null
  selected_trap: string | null
  record: {
    id: string
    questionId: string
    questionType: string
    userAnswer: string
    correctAnswer: string
    isCorrect: boolean
    trapType: string
    time: string
  } | null
  tool_trace: ToolCall[]
}

export interface FullQuestion {
  id: string
  number: number
  questionType: string
  content: string
  options: Record<string, string>
  correctAnswer: string
  analysis: Record<string, { trapType: string; explanation: string }>
  steps: string[]
  location: string
  sourceSentence: string
  sourceHighlights: string[]
  passage: string
  passageId: string
  year: number
  examType: string
  textNumber: number
}

export interface ImportExamPayload {
  year: number
  exam_type: string
  text_number: number
  passage: string
  question_type: string
  content: string
  options: Record<string, string>
  correct_answer: string
}

export interface AutoImportPayload {
  url?: string
  text?: string
  year: number
  exam_type: string
  text_number: number
  answer_key?: string
}

export interface AutoImportResponse {
  ok: boolean
  passage_id: string
  question_ids: string[]
  analysis_source: 'deepseek' | 'fallback'
  answer_source: 'provided' | 'inferred'
  questions: FullQuestion[]
}

export interface ImportExamResponse {
  ok: boolean
  question_id: string
  passage_id: string
  analysis_source: 'deepseek' | 'fallback'
  question: FullQuestion
}

export interface ChatSection {
  title: string
  body?: string
  items?: string[]
  code?: string
}

export interface ChatWorkflow {
  intro: string
  sections: ChatSection[]
  tool_trace: ToolCall[]
  citations: Citation[]
  llm_used?: boolean
}

export interface MetaInfo {
  vocab_count: number
  sentence_count: number
  question_count: number
  passage_count: number
  trap_count: number
  wordbook_count: number
  record_count: number
  database: string
  knowledge_version: string
}

export interface AppState {
  words: Word[]
  records: StudyRecord[]
}

export interface RareWord {
  word: string
  basic_meaning: string
  rare_meaning: string
  level: string
  exam_frequency: number
}

export interface KnowledgeResponse {
  traps: {
    name: string
    definition: string
    signals: string
    example: string
    tone: string
  }[]
  rare_words: RareWord[]
  meta: MetaInfo
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })
  if (!response.ok) {
    const detail = await response.text().catch(() => '')
    throw new Error(
      `API ${response.status}${detail ? `: ${detail.slice(0, 160)}` : ''}`,
    )
  }
  return (await response.json()) as T
}

export const api = {
  getHealth: () => request<{ status: string } & MetaInfo>('/health'),
  getMeta: () => request<MetaInfo>('/meta'),
  getState: () => request<AppState>('/state'),
  getKnowledge: () => request<KnowledgeResponse>('/knowledge'),
  getQuestionsFull: () => request<{ items: FullQuestion[] }>('/questions/full'),
  importExam: (payload: ImportExamPayload) =>
    request<ImportExamResponse>('/exams/import', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  autoImportExam: (payload: AutoImportPayload) =>
    request<AutoImportResponse>('/exams/auto-import', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  runSentence: (sentenceId: string) =>
    request<SentenceWorkflow>('/workflow/sentence', {
      method: 'POST',
      body: JSON.stringify({ sentence_id: sentenceId }),
    }),

  runOptions: (questionId: string, userAnswer?: string | null) =>
    request<OptionWorkflow>('/workflow/options', {
      method: 'POST',
      body: JSON.stringify({
        question_id: questionId,
        user_answer: userAnswer ?? null,
      }),
    }),

  chat: (message: string, contextId = '2024_en1_t1') =>
    request<ChatWorkflow>('/workflow/chat', {
      method: 'POST',
      body: JSON.stringify({ message, context_id: contextId }),
    }),

  addWord: (payload: {
    spelling: string
    meaning: string
    source?: string
    context?: string
  }) =>
    request<{ ok: boolean; word: Word }>('/wordbook', {
      method: 'POST',
      body: JSON.stringify({
        spelling: payload.spelling,
        meaning: payload.meaning,
        source: payload.source ?? '',
        context: payload.context ?? '',
      }),
    }),

  deleteWord: (spelling: string) =>
    request<{ ok: boolean }>(`/wordbook/${encodeURIComponent(spelling)}`, {
      method: 'DELETE',
    }),

  reviewWord: (spelling: string, remembered: boolean) =>
    request<{ ok: boolean; word: Word }>('/wordbook/review', {
      method: 'POST',
      body: JSON.stringify({ spelling, remembered }),
    }),

  addRecord: (payload: {
    questionId: string
    questionType: string
    userAnswer: string
    correctAnswer: string
  }) =>
    request<{ ok: boolean }>('/records', {
      method: 'POST',
      body: JSON.stringify({
        question_id: payload.questionId,
        question_type: payload.questionType,
        user_answer: payload.userAnswer,
        correct_answer: payload.correctAnswer,
      }),
    }),

  getReport: () => request<Record<string, unknown>>('/report'),
}
