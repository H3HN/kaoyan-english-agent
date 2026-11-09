const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? '/api'
const TOKEN_KEY = 'kaoyan-admin-token'

export class AdminAuthError extends Error {
  constructor() {
    super('管理员令牌无效')
    this.name = 'AdminAuthError'
  }
}

export function getAdminToken(): string {
  return window.localStorage.getItem(TOKEN_KEY) ?? ''
}

export function setAdminToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token)
}

export function clearAdminToken(): void {
  window.localStorage.removeItem(TOKEN_KEY)
}

export interface AdminStats {
  draft: number
  reviewed: number
  published: number
  total: number
  question_total: number
  sentence_total: number
}

export interface AdminPassage {
  id: string
  year: number
  exam_type: string
  text_number: number
  publication_status: 'draft' | 'reviewed' | 'published'
  status_label: string
  revision: number
  reviewed_by: string
  reviewed_at: string
  published_at: string
  question_count: number
  sentence_count: number
  last_event_at: string | null
}

export interface AdminPage {
  items: AdminPassage[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface AdminEvent {
  id: number
  passage_id: string
  revision: number
  action: string
  actor: string
  created_at: string
}

export interface AdminPassageDetail extends AdminPassage {
  review_issues: string[]
  practice_issues: string[]
  entry: Record<string, unknown>
}

export interface AdminImportItemResult {
  index: number
  ok: boolean
  passage_id?: string
  revision?: number
  publication_status?: string
  error?: string
}

export interface AdminImportResult {
  ok: boolean
  succeeded: number
  failed: number
  results: AdminImportItemResult[]
}

export interface VocabEntry {
  id: number
  word: string
  phonetic: string
  basic_meaning: string
  rare_meaning: string
  exam_frequency: number
  level: string
  enabled: boolean
}

export interface VocabCitation {
  sentence_id: string
  source: string
  text: string
  year: number
  exam_type: string
  question_type: string
}

export interface VocabDetail extends VocabEntry {
  citations: VocabCitation[]
}

export interface VocabPage {
  items: VocabEntry[]
  total: number
  page: number
  page_size: number
  pages: number
  stats: { total: number; enabled: number; disabled: number }
}

export interface VocabPayload {
  word: string
  phonetic: string
  basic_meaning: string
  rare_meaning: string
  exam_frequency: number
  level: string
  enabled: boolean
}

export interface TrapRule {
  id: number
  name: string
  definition: string
  signals: string
  example: string
  tone: string
}

export interface TrapPayload {
  name: string
  definition: string
  signals: string
  example: string
  tone: string
}

export interface MonitorCount {
  date: string
  count: number
}

export interface MonitorWorkflow {
  workflow: string
  count: number
}

export interface MonitorTypeStat {
  type: string
  total: number
  correct: number
  accuracy: number
}

export interface MonitorResponse {
  days: number
  runs: {
    total: number
    by_workflow: MonitorWorkflow[]
    daily: MonitorCount[]
  }
  practice: {
    total: number
    correct: number
    accuracy: number
    by_type: MonitorTypeStat[]
    daily: MonitorCount[]
  }
  breakdowns: { total: number; llm_used: number; llm_ratio: number }
  wordbook: { total: number; due: number }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-Admin-Token': getAdminToken(),
      ...(init?.headers ?? {}),
    },
  })
  if (!response.ok) {
    if (response.status === 401) throw new AdminAuthError()
    const body = await response.json().catch(() => null)
    const detail = body?.detail
    const message =
      typeof detail === 'string'
        ? detail
        : detail?.message
          ? [detail.message, ...(detail.issues ?? [])].filter(Boolean).join('；')
          : `API ${response.status}：请求失败`
    throw new Error(message)
  }
  return (await response.json()) as T
}

export const adminApi = {
  getStats: () => request<AdminStats>('/admin/stats'),

  listPassages: (params: {
    status?: string
    q?: string
    page?: number
    pageSize?: number
  }) => {
    const search = new URLSearchParams()
    if (params.status) search.set('status', params.status)
    if (params.q) search.set('q', params.q)
    search.set('page', String(params.page ?? 1))
    search.set('page_size', String(params.pageSize ?? 20))
    return request<AdminPage>(`/admin/passages?${search.toString()}`)
  },

  getPassage: (id: string) =>
    request<AdminPassageDetail>(`/admin/passages/${encodeURIComponent(id)}`),

  getEvents: (id: string) =>
    request<{ items: AdminEvent[] }>(
      `/admin/passages/${encodeURIComponent(id)}/events`,
    ),

  importDocument: (document: unknown, actor = '管理员') =>
    request<AdminImportResult>('/admin/passages/import', {
      method: 'POST',
      body: JSON.stringify({ document, actor }),
    }),

  transition: (id: string, action: string, actor = '管理员') =>
    request<{
      id: string
      publication_status: string
      revision: number
      reviewed_by: string
      reviewed_at: string
      published_at: string
    }>(`/admin/passages/${encodeURIComponent(id)}/transition`, {
      method: 'POST',
      body: JSON.stringify({ action, actor }),
    }),

  listVocab: (params: {
    keyword?: string
    level?: string
    enabled?: string
    page?: number
    pageSize?: number
  }) => {
    const search = new URLSearchParams()
    if (params.keyword) search.set('keyword', params.keyword)
    if (params.level) search.set('level', params.level)
    if (params.enabled) search.set('enabled', params.enabled)
    search.set('page', String(params.page ?? 1))
    search.set('page_size', String(params.pageSize ?? 20))
    return request<VocabPage>(`/admin/vocab?${search.toString()}`)
  },

  getVocab: (word: string) =>
    request<VocabDetail>(`/admin/vocab/${encodeURIComponent(word)}`),

  createVocab: (payload: VocabPayload) =>
    request<VocabDetail>('/admin/vocab', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateVocab: (word: string, payload: VocabPayload) =>
    request<VocabDetail>(`/admin/vocab/${encodeURIComponent(word)}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  toggleVocab: (word: string, enabled: boolean) =>
    request<VocabDetail>(
      `/admin/vocab/${encodeURIComponent(word)}/toggle`,
      { method: 'POST', body: JSON.stringify({ enabled }) },
    ),

  listTrapRules: () => request<{ items: TrapRule[] }>('/admin/trap-rules'),

  createTrapRule: (payload: TrapPayload) =>
    request<TrapRule>('/admin/trap-rules', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateTrapRule: (id: number, payload: TrapPayload) =>
    request<TrapRule>(`/admin/trap-rules/${id}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  getMonitor: () => request<MonitorResponse>('/admin/monitor'),
}