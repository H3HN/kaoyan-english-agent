import type { QuestionType } from './content'
import type { StudyRecord, Word } from '../types'

const inDays = (days: number) =>
  new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString()

export const seedWords: Word[] = [
  {
    id: 'w-ubiquitous',
    spelling: 'ubiquitous',
    phonetic: '/juːˈbɪkwɪtəs/',
    meaning: 'adj. 无处不在的；普遍存在的',
    source: '2024 英语一 · Text 1',
    isOutline: true,
    familiarity: 0.75,
    reviewCount: 3,
    nextReview: inDays(2),
  },
  {
    id: 'w-trajectory',
    spelling: 'trajectory',
    phonetic: '/trəˈdʒektəri/',
    meaning: 'n. 轨迹；发展路径',
    source: '2023 英语一 · Text 1',
    isOutline: true,
    familiarity: 0.45,
    reviewCount: 2,
    nextReview: inDays(-1),
  },
  {
    id: 'w-deteriorate',
    spelling: 'deteriorate',
    phonetic: '/dɪˈtɪəriəreɪt/',
    meaning: 'v. 恶化；退化',
    source: '2023 英语一 · Text 1',
    isOutline: true,
    familiarity: 0.3,
    reviewCount: 1,
    nextReview: inDays(-2),
  },
  {
    id: 'w-encompass',
    spelling: 'encompass',
    phonetic: '/ɪnˈkʌmpəs/',
    meaning: 'v. 包含；涵盖',
    source: '2024 英语一 · Text 1',
    isOutline: true,
    familiarity: 0.6,
    reviewCount: 2,
    nextReview: inDays(4),
  },
  {
    id: 'w-scrutiny',
    spelling: 'scrutiny',
    phonetic: '/ˈskruːtəni/',
    meaning: 'n. 仔细审查；监督',
    source: '2024 英语一 · Text 1',
    isOutline: true,
    familiarity: 0.2,
    reviewCount: 1,
    nextReview: inDays(-1),
  },
  {
    id: 'w-accountability',
    spelling: 'accountability',
    phonetic: '/əˌkaʊntəˈbɪləti/',
    meaning: 'n. 问责制；责任',
    source: '2024 英语一 · Text 1',
    isOutline: true,
    familiarity: 0.85,
    reviewCount: 4,
    nextReview: inDays(7),
  },
  {
    id: 'w-perpetuate',
    spelling: 'perpetuate',
    phonetic: '/pəˈpetʃueɪt/',
    meaning: 'v. 使持续；使永久化',
    source: '2023 英语一 · Text 1',
    isOutline: true,
    familiarity: 0.5,
    reviewCount: 2,
    nextReview: inDays(-0.1),
  },
]

const recordPatterns: { type: QuestionType; results: boolean[] }[] = [
  { type: '主旨题', results: [true, true, false, true, true, true] },
  { type: '细节题', results: [true, true, true, false, true] },
  { type: '推理题', results: [true, false, false, true] },
  { type: '词义题', results: [true, false, true] },
  { type: '态度题', results: [false, true] },
]

const flatRecords = recordPatterns.flatMap(({ type, results }) =>
  results.map((isCorrect) => ({ type, isCorrect })),
)

const dayOffsets = [0, 0, 1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 5, 6, 6, 6, 1]

export const seedRecords: StudyRecord[] = flatRecords
  .map((item, index) => ({
    id: `seed-r${index + 1}`,
    questionId: `seed-q${index + 1}`,
    questionType: item.type,
    userAnswer: item.isCorrect ? 'B' : index % 2 === 0 ? 'A' : 'C',
    correctAnswer: 'B',
    isCorrect: item.isCorrect,
    time: new Date(
      Date.now() -
        dayOffsets[index] * 24 * 60 * 60 * 1000 -
        (index % 9) * 37 * 60 * 1000,
    ).toISOString(),
  }))
  .sort((a, b) => b.time.localeCompare(a.time))
