import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { StudyRecord, Word } from '../types'
import { seedRecords, seedWords } from '../data/seeds'
import type { QuestionType } from '../data/content'
import { api } from '../lib/api'

export const REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]
const STORAGE_KEY = 'kaoyan-studio-v1'

interface PersistedState {
  words: Word[]
  records: StudyRecord[]
}

interface AppStoreValue {
  words: Word[]
  records: StudyRecord[]
  dueWords: Word[]
  connected: boolean
  refresh: () => Promise<void>
  addWord: (input: {
    spelling: string
    meaning: string
    source?: string
    context?: string
  }) => { ok: boolean; message: string }
  removeWord: (id: string) => void
  reviewWord: (id: string, remembered: boolean) => void
  addRecord: (input: {
    questionId: string
    questionType: QuestionType
    userAnswer: string
    correctAnswer: string
  }) => StudyRecord
}

const AppStoreContext = createContext<AppStoreValue | null>(null)

function loadPersistedState(): PersistedState | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw) as Partial<PersistedState>
    if (!Array.isArray(parsed.words) || !Array.isArray(parsed.records)) {
      return null
    }
    return { words: parsed.words, records: parsed.records }
  } catch {
    return null
  }
}

export function AppStoreProvider({ children }: { children: ReactNode }) {
  const persisted = loadPersistedState()
  const [words, setWords] = useState<Word[]>(
    () => persisted?.words ?? seedWords,
  )
  const [records, setRecords] = useState<StudyRecord[]>(
    () => persisted?.records ?? seedRecords,
  )
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    try {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ words, records }),
      )
    } catch {
      // Storage can be unavailable in private browsing; demo still works in memory.
    }
  }, [words, records])

  const refresh = useCallback(async () => {
    try {
      const data = await api.getState()
      setWords(data.words)
      setRecords(data.records)
      setConnected(true)
    } catch {
      setConnected(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const dueWords = useMemo(
    () =>
      words
        .filter((word) => new Date(word.nextReview).getTime() <= Date.now())
        .sort(
          (a, b) =>
            new Date(a.nextReview).getTime() - new Date(b.nextReview).getTime(),
        ),
    [words],
  )

  const addWord = useCallback(
    (input: {
      spelling: string
      meaning: string
      source?: string
      context?: string
    }) => {
      const spelling = input.spelling.trim()
      const meaning = input.meaning.trim()
      if (!spelling) return { ok: false, message: '请先输入单词。' }
      if (!meaning) return { ok: false, message: '请补充中文释义。' }
      if (
        words.some(
          (word) => word.spelling.toLowerCase() === spelling.toLowerCase(),
        )
      ) {
        return { ok: false, message: `“${spelling}”已经在单词本中。` }
      }

      const word: Word = {
        id: `w-${Date.now()}`,
        spelling,
        phonetic: '',
        meaning,
        source: input.source?.trim() || '手动添加',
        isOutline: true,
        familiarity: 0,
        reviewCount: 0,
        nextReview: new Date(
          Date.now() + REVIEW_INTERVALS[0] * 24 * 60 * 60 * 1000,
        ).toISOString(),
      }
      setWords((prev) => [word, ...prev])

      // 后端是持久化来源；本地先乐观更新，失败时保留演示态。
      void api
        .addWord({
          spelling,
          meaning,
          source: word.source,
          context: input.context?.trim() || '手动添加',
        })
        .then((response) => {
          if (!response.word) return
          setWords((prev) =>
            prev.map((item) =>
              item.spelling.toLowerCase() === spelling.toLowerCase()
                ? {
                    ...item,
                    id: response.word.id,
                    nextReview: response.word.nextReview,
                    meaning: response.word.meaning,
                  }
                : item,
            ),
          )
          setConnected(true)
        })
        .catch(() => setConnected(false))

      return {
        ok: true,
        message: `已添加“${spelling}”，首次复习安排在明天。`,
      }
    },
    [words],
  )

  const removeWord = useCallback(
    (id: string) => {
      const target = words.find((word) => word.id === id)
      setWords((prev) => prev.filter((word) => word.id !== id))
      if (target) {
        void api.deleteWord(target.spelling).catch(() => setConnected(false))
      }
    },
    [words],
  )

  const reviewWord = useCallback(
    (id: string, remembered: boolean) => {
      const target = words.find((word) => word.id === id)
      setWords((prev) =>
        prev.map((word) => {
          if (word.id !== id) return word
          const nextCount = word.reviewCount + 1
          const interval = remembered
            ? REVIEW_INTERVALS[
                Math.min(nextCount - 1, REVIEW_INTERVALS.length - 1)
              ]
            : 1
          return {
            ...word,
            reviewCount: nextCount,
            familiarity: remembered
              ? Math.min(1, word.familiarity + 0.15)
              : Math.max(0, word.familiarity - 0.1),
            nextReview: new Date(
              Date.now() + interval * 24 * 60 * 60 * 1000,
            ).toISOString(),
          }
        }),
      )
      if (target) {
        void api
          .reviewWord(target.spelling, remembered)
          .then(() => setConnected(true))
          .catch(() => setConnected(false))
      }
    },
    [words],
  )

  const addRecord = useCallback(
    (input: {
      questionId: string
      questionType: QuestionType
      userAnswer: string
      correctAnswer: string
    }) => {
      const record: StudyRecord = {
        id: `r-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
        questionId: input.questionId,
        questionType: input.questionType,
        userAnswer: input.userAnswer,
        correctAnswer: input.correctAnswer,
        isCorrect: input.userAnswer === input.correctAnswer,
        time: new Date().toISOString(),
      }
      setRecords((prev) => [record, ...prev])
      // 选项分析工作流会同时把错题写入后端 practice_records，
      // 这里只做前端即时镜像，避免重复记录。
      return record
    },
    [],
  )

  const value = useMemo(
    () => ({
      words,
      records,
      dueWords,
      connected,
      refresh,
      addWord,
      removeWord,
      reviewWord,
      addRecord,
    }),
    [
      words,
      records,
      dueWords,
      connected,
      refresh,
      addWord,
      removeWord,
      reviewWord,
      addRecord,
    ],
  )

  return (
    <AppStoreContext.Provider value={value}>
      {children}
    </AppStoreContext.Provider>
  )
}

export function useAppStore() {
  const value = useContext(AppStoreContext)
  if (!value) {
    throw new Error('useAppStore must be used within AppStoreProvider')
  }
  return value
}
