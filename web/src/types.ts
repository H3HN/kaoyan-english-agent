import type { QuestionType } from './data/content'

export interface Word {
  id: string
  spelling: string
  phonetic: string
  meaning: string
  source: string
  isOutline: boolean
  familiarity: number
  reviewCount: number
  nextReview: string
}

export interface StudyRecord {
  id: string
  questionId: string
  questionType: QuestionType
  userAnswer: string
  correctAnswer: string
  isCorrect: boolean
  time: string
}
