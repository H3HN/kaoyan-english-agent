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

export interface VocabRow {
  word: string
  basic_meaning: string
  rare_meaning: string | null
  level: string
  exam_frequency: number
}

export interface VocabListResponse {
  items: VocabRow[]
  total: number
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
  analysis?: Partial<Record<string, { trapType?: string | null; explanation?: string | null } | null>> | null
  steps?: string[] | null
  location: string
  sourceSentence: string
  sourceSentenceId?: string | null
  answerSource?: 'provided' | 'inferred' | 'manual' | 'unknown'
  answerSourceNote?: string
  reviewStatus?: string
  locationStatus?: string
  sourceQuote?: string
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
  answer_source_note?: string
}

export interface AutoImportResponse {
  ok: boolean
  passage_id: string
  question_ids: string[]
  analysis_source: 'deepseek' | 'fallback'
  answer_source: 'provided' | 'inferred'
  review_status?: string
  warnings?: string[]
  questions: FullQuestion[]
}

export interface ImportExamResponse {
  ok: boolean
  question_id: string
  passage_id: string
  analysis_source: 'deepseek' | 'fallback'
  question: FullQuestion
}


export interface PassageSummary {
  id: string
  year: number
  exam_type: string
  text_number: number
  char_count: number
  preview: string
  sentence_count: number
  question_count: number
  imported: boolean
}

export interface PassageSentence {
  id: string
  index: number
  paragraph: number
  text: string
  source: string
  word_count: number
  is_long: boolean
}

export interface BreakdownNode {
  role: string
  label: string
  children?: BreakdownNode[]
}

export interface SentenceBreakdown {
  id: string
  index: number
  source: string
  original: string
  wordCount: number
  isLong: boolean
  main: string
  mainNote: string
  clauseNote: string
  clauses: { text: string; label: string; note: string }[]
  modifiers: { text: string; label: string; note: string }[]
  translation: string
  translationLayers: string[]
  grammar: { name: string; note: string }[]
  examPoints: string[]
  tree: BreakdownNode[]
  segments: { text: string; tone: string; label?: string }[]
  llmUsed: boolean
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


export type AgentRoute =
  | '/studio'
  | '/dashboard'
  | '/reading'
  | '/sentence'
  | '/vocab'
  | '/analytics'
  | '/library'

export interface ClientContext {
  current_route: AgentRoute
  active_passage_id: string | null
  active_passage_label?: string | null
  active_question_id: string | null
  active_sentence_id: string | null
  selected_raw_text: string | null
  active_sentence_data?: AdHocSentenceData | null
  active_sentence_source_type?: string | null
  active_content_type?: 'reader' | 'paragraph' | 'listening' | 'writing' | null
  active_content_title?: string | null
  active_content_text?: string | null
  trigger_mode: 'USER_CHAT' | 'AUTO_EVENT'
  recent_event?: {
    event_type: 'QUESTION_SUBMITTED' | 'SENTENCE_SELECTED' | 'PASSAGE_FINISHED'
    question_id?: string
    user_choice?: 'A' | 'B' | 'C' | 'D'
    correct_choice?: 'A' | 'B' | 'C' | 'D'
    is_correct?: boolean
    trap_type?: string
  } | null
}


export type StudioTier = 'word' | 'phrase' | 'sentence' | 'paragraph' | 'passage' | 'plan'

export interface WordInsightData {
  word: string
  phonetic: string
  level: string
  exam_frequency: number
  basic_meaning: string
  rare_meaning: string | null
  is_phrase: boolean
  collocations: string[]
  examples: {
    sentence_id: string
    source: string
    text: string
    translation?: string
  }[]
  lookup_source?: 'local' | 'llm' | 'none'
  part_of_speech?: string
  is_proper_noun?: boolean
}

export interface ParagraphSentence {
  index: number
  text: string
  translation: string
  logic: string
  logic_note: string
  stars: number
}

export interface ParagraphData {
  paragraph_en: string
  source_label: string
  main_idea: string
  topic_sentence: string
  sentences: ParagraphSentence[]
  logic_flow: { from: number; to: number; label: string }[]
  vocabulary: { word: string; meaning: string; rare_meaning?: string | null; sentence: string }[]
}


export type WorkspaceTier =
  | 'word'
  | 'phrase'
  | 'sentence'
  | 'paragraph'
  | 'plan'
  | 'vocab'
  | 'reading'
  | 'listening'
  | 'writing'
  | 'reader'
  | 'home'

export interface WorkspaceUnit {
  id: string
  tier: WorkspaceTier
  label: string
  data: unknown
  saved?: boolean
  examSentenceId?: string | null
}

export interface CanvasCommand {
  op: 'replace' | 'push' | 'update'
  unit: WorkspaceUnit
}

export interface AdHocSentenceData {
  sentence_en: string
  source_label: string
  word_count?: number
  step1_trunk: string
  step2_clauses: { text: string; label: string; note: string }[]
  step3_modifiers: { text: string; label: string; note: string }[]
  step4_translation: string
  step4_translation_layers?: string[]
  step5_vocab_and_grammar: {
    vocabulary?: { word: string; meaning: string; rare_meaning?: string | null }[]
    grammar?: { name: string; note: string }[]
    exam_points?: string[]
  }
}

export interface AdHocReadingData {
  passage_text: string
  question_text: string
  options: Record<string, string>
  analysis: Record<string, { trapType: string; explanation: string }>
  correct_answer: string
  question_type: string
  steps: string[]
  source_label: string
}

export interface AdHocVocabData {
  source_text: string
  added: { word: string; meaning: string; rare?: string | null; source?: string }[]
  words?: { word: string; meaning: string; rare?: string | null; source?: string; status?: 'new' | 'existing' }[]
  skipped: number
  total: number
}

export type ClientActionType =
  | 'NAVIGATE_TO'
  | 'HIGHLIGHT_SENTENCE'
  | 'REVEAL_OPTION_ANALYSIS'
  | 'OPEN_FLASHCARD_DRAWER'
  | 'REFRESH_QUERY'
  | 'SAVE_SENTENCE_STATE'
  | 'WORD_ADDED'
  | 'APPLY_CANVAS_COMMAND'

export interface ClientAction {
  action_type: ClientActionType
  payload: Record<string, unknown>
}

export type AgentWidgetType =
  | 'PASSAGE_RECOMMEND'
  | 'TRAP_DIAGNOSIS'
  | 'VOCAB_BATCH_SAVED'
  | 'SCHEDULE_PLAN'

export interface AgentWidget {
  widget_type: AgentWidgetType
  data: Record<string, unknown>
}

export interface AgentResponse {
  intro: string
  sections: ChatSection[]
  tool_trace: ToolCall[]
  citations: Citation[]
  client_actions: ClientAction[]
  widgets: AgentWidget[]
  llm_used?: boolean
}


export interface ScheduleTask {
  id: number
  scheduled_date: string
  day_label: string
  task_type: string
  title: string
  agent_reason: string
  target_route: string
  target_resource_id: string | null
  status: 'pending' | 'completed'
  created_at: string
}



export interface TrapMethodCard {
  name: string
  tone: string
  definition: string
  signals: string[]
  steps: string[]
  correct_pattern: string
  question_types: string[]
}

export interface LearnerProfile {
  total_attempts: number
  correct: number
  accuracy: number
  trap_counts: Record<string, number>
  weakest_trap: string | null
  weakest_trap_card: TrapMethodCard | null
  by_question_type: { question_type: string; total: number; accuracy: number }[]
}

export interface SentenceLibraryItem {
  id: string
  sentence_en: string
  preview: string
  source_label: string
  grammar_tags: string[]
  source_type: 'EXAM_FEATURED' | 'USER_SAVED'
  updated_at?: string
}

export interface SavedSentenceAnalysis {
  id: string
  exam_sentence_id: string | null
  sentence_en: string
  source_type: string
  source_label: string
  data: AdHocSentenceData
  saved: boolean
  updated_at: string
}

export interface SentenceLibraryResponse {
  featured: SentenceLibraryItem[]
  saved: SentenceLibraryItem[]
}

export interface SaveSentenceResponse {
  ok: boolean
  analysis_id: string
  source_type: string
  source_label: string
  saved: boolean
}



export type VocabQuizMode = 'choice' | 'spelling' | 'listening' | 'context'

export interface VocabQuizItem {
  mode: VocabQuizMode
  word: string
  meaning: string
  context: string
  source: string
  options: string[]
  answer: string
  prompt: string
}


export interface ReaderData {
  title: string
  text: string
  source_label: string
  source_url?: string
  license?: string
  source_id?: number
}

export interface ReaderSource {
  id: number
  title: string
  source_url: string
  license: string
  status: 'draft' | 'published'
  created_at: string
  published_at: string
  word_count: number
  preview: string
  text?: string
}

export interface ListeningData {
  source_label: string
  sentences: { index: number; text: string }[]
}

export interface WritingData {
  source_label: string
  prompt: string
  draft: string
}

export interface WritingIssue {
  type: string
  quote: string
  suggestion: string
  reason: string
}

export interface WritingFeedback {
  scores: Record<string, number>
  summary: string
  issues: WritingIssue[]
  minimum_revision: string
  rewrite_excerpt: string
  next_action: string
  llm_used?: boolean
}

export interface LearnerGoal {
  target_score: number
  exam_date: string
  daily_minutes: number
  current_level: string
  updated_at?: string
}

export interface ReadingSession {
  id: number
  passage_id: string
  started_at: string
  duration_seconds: number
  answered: number
  correct: number
  accuracy: number
  created_at: string
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
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map((item: { msg?: string }) => item.msg ?? '字段无效').join('；')
        : [detail?.message, ...(detail?.issues ?? [])].filter(Boolean).join('；')
    throw new Error(message || `API ${response.status}：请求失败`)

  }
  return (await response.json()) as T
}

export const api = {
  getHealth: () => request<{ status: string } & MetaInfo>('/health'),
  getMeta: () => request<MetaInfo>('/meta'),
  getState: () => request<AppState>('/state'),
  getKnowledge: () => request<KnowledgeResponse>('/knowledge'),
  getQuestionsFull: () => request<{ items: FullQuestion[] }>('/questions/full'),
  getPassages: () => request<{ items: PassageSummary[] }>('/passages'),
  getSentenceLibrary: () => request<SentenceLibraryResponse>('/sentences/library'),
  getTrapCards: () => request<{ items: TrapMethodCard[] }>('/trap-cards'),
  getReaderSources: (status?: 'draft' | 'published') =>
    request<{ items: ReaderSource[] }>(`/reader/sources${status ? `?status=${status}` : ''}`),
  getReaderSource: (id: number) => request<ReaderSource>(`/reader/sources/${id}`),
  importReaderSource: (payload: { title: string; text: string; source_url?: string; license?: string }) =>
    request<{ ok: boolean; source: ReaderSource }>('/reader/import', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  publishReaderSource: (id: number) =>
    request<{ ok: boolean; source: ReaderSource }>(`/reader/sources/${id}/publish`, {
      method: 'POST',
    }),
  getVocabQuiz: (mode: VocabQuizMode, limit = 8) =>
    request<{ items: VocabQuizItem[] }>(`/vocab/quiz?mode=${mode}&limit=${limit}`),
  getLearnerGoal: () => request<{ goal: LearnerGoal | null }>('/learner/goal'),
  saveLearnerGoal: (goal: Omit<LearnerGoal, 'updated_at'>) =>
    request<{ ok: boolean; goal: LearnerGoal }>('/learner/goal', {
      method: 'PUT',
      body: JSON.stringify(goal),
    }),
  saveReadingSession: (payload: {
    passage_id: string
    started_at: string
    duration_seconds: number
    answered: number
    correct: number
  }) =>
    request<{ ok: boolean; session: ReadingSession }>('/reading/sessions', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getTrapCard: (name: string) =>
    request<TrapMethodCard>(`/trap-cards/${encodeURIComponent(name)}`),
  getLearnerProfile: () => request<LearnerProfile>('/learner/profile'),
  reviewWriting: (payload: { prompt: string; draft: string }) =>
    request<WritingFeedback>('/writing/review', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getSentenceAnalysis: (analysisId: string) =>
    request<SavedSentenceAnalysis>(`/sentences/analyses/${encodeURIComponent(analysisId)}`),
  saveSentence: (payload: {
    sentence_en: string
    source_label: string
    exam_sentence_id?: string | null
    sentence_data: AdHocSentenceData
  }) =>
    request<SaveSentenceResponse>('/sentences/save', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  addWordFromSentence: (payload: {
    word: string
    sentence_en: string
    sentence_data: AdHocSentenceData
    analysis_id?: string | null
    source_label?: string
  }) =>
    request<{ ok: boolean; word: Word; analysis_id: string; sentence_saved: boolean }>(
      '/wordbook/from-sentence',
      { method: 'POST', body: JSON.stringify(payload) },
    ),
  getSchedule: () => request<{ items: ScheduleTask[] }>('/schedule'),
  completeScheduleTask: (taskId: number, completed = true) =>
    request<{ ok: boolean; task: ScheduleTask }>(`/schedule/${taskId}/complete`, {
      method: 'POST',
      body: JSON.stringify({ completed }),
    }),
  browseVocab: (params: {
    q?: string
    level?: string
    sort?: 'freq' | 'alpha'
    offset?: number
    limit?: number
  }) => {
    const search = new URLSearchParams()
    if (params.q) search.set('q', params.q)
    if (params.level) search.set('level', params.level)
    if (params.sort) search.set('sort', params.sort)
    search.set('offset', String(params.offset ?? 0))
    search.set('limit', String(params.limit ?? 50))
    return request<VocabListResponse>(`/vocab?${search.toString()}`)
  },
  getPassageSentences: (passageId: string) =>
    request<{ passage: Omit<PassageSummary, 'char_count' | 'preview' | 'sentence_count' | 'question_count' | 'imported'>; items: PassageSentence[] }>(
      `/passages/${encodeURIComponent(passageId)}/sentences`,
    ),
  getSentenceBreakdown: (sentenceId: string) =>
    request<SentenceBreakdown>(
      `/sentences/${encodeURIComponent(sentenceId)}/breakdown`,
    ),
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

  agentChat: (message: string, clientContext: ClientContext) =>
    request<AgentResponse>('/agent/chat', {
      method: 'POST',
      body: JSON.stringify({ message, client_context: clientContext, trigger_mode: clientContext.trigger_mode }),
    }),

  chat: (message: string, contextId: string) =>
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

  reviewWord: (spelling: string, quality: number) =>
    request<{ ok: boolean; word: Word }>('/wordbook/review', {
      method: 'POST',
      body: JSON.stringify({ spelling, quality }),
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
