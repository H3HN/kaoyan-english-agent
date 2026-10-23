export type QuestionType = '主旨题' | '细节题' | '推理题' | '词义题' | '态度题'
export type OptionKey = 'A' | 'B' | 'C' | 'D'
export type Tone = 'blue' | 'emerald' | 'cyan' | 'amber' | 'violet' | 'red' | 'slate'

export interface OptionAnalysis {
  trapType: string
  explanation: string
}

export interface RawQuestion {
  number: number
  questionType: QuestionType
  content: string
  options: Record<OptionKey, string>
  correctAnswer: OptionKey
  analysis: Record<OptionKey, OptionAnalysis>
  steps: string[]
}

export interface Passage {
  id: string
  year: number
  examType: string
  textNumber: number
  passage: string
  questions: RawQuestion[]
}

export interface Question extends RawQuestion {
  id: string
  passageId: string
  year: number
  examType: string
  textNumber: number
  location: string
  sourceSentence: string
  sourceHighlights: string[]
}

export interface Segment {
  text: string
  tone: Tone
  label?: string
}

export interface Clause {
  label: string
  text: string
  note: string
}

export interface Modifier {
  label: string
  text: string
  note: string
}

export interface TreeNode {
  label: string
  role: string
  children?: TreeNode[]
}

export interface SentenceAnalysis {
  id: string
  index: number
  source: string
  original: string
  isLong: boolean
  segments: Segment[]
  main: string
  mainNote: string
  clauses: Clause[]
  clauseNote: string
  modifiers: Modifier[]
  translation: string
  translationLayers: string[]
  grammar: { name: string; note: string }[]
  examPoints: string[]
  tree: TreeNode[]
}

export const passages: Passage[] = [
  {
    id: '2024_en1_t1',
    year: 2024,
    examType: '英语一',
    textNumber: 1,
    passage:
      'The rise of artificial intelligence has prompted both excitement and anxiety in equal measure. Proponents argue that AI will revolutionize industries, streamline processes, and create new categories of jobs that we cannot yet imagine. Critics, however, warn that the rapid deployment of AI systems could lead to widespread job displacement, particularly among workers whose roles involve routine, repetitive tasks. What remains clear is that the technology which once seemed confined to the realm of science fiction has now become an inescapable part of our daily lives, raising questions about privacy, accountability, and the very definition of human capability.',
    questions: [
      {
        number: 1,
        questionType: '主旨题',
        content: 'What is the main idea of the passage?',
        options: {
          A: 'AI will definitely create more jobs than it eliminates.',
          B: 'AI technology has both positive and negative implications for society.',
          C: 'AI is only beneficial to industries that rely on repetitive tasks.',
          D: 'AI technology will soon replace all human workers.',
        },
        correctAnswer: 'B',
        analysis: {
          A: {
            trapType: '过于绝对',
            explanation:
              '文中说 proponents argue（支持者主张），并非 definitely（确定），将可能变为必然。',
          },
          B: {
            trapType: '正确',
            explanation:
              '文章既讲 excitement 又讲 anxiety，既讲 revolutionize 又讲 job displacement，全面概括正反两面。',
          },
          C: {
            trapType: '缩小范围',
            explanation:
              '文中说 AI 将 revolutionize industries（颠覆各行业），并非 only beneficial to repetitive tasks（仅对重复任务有益），缩小了范围。',
          },
          D: {
            trapType: '过于绝对',
            explanation:
              '文中说 job displacement（岗位取代），并非 replace all human workers（取代所有人类工人），过于绝对。',
          },
        },
        steps: [
          '识别题型：主旨题，需要概括全文核心观点。',
          '分析文章结构：首句提出 excitement 与 anxiety，中间分别论述正反两面，最后总结 AI 已成为现实并引发深层问题。',
          '排除 A、D：过于绝对（definitely / all），与文中谨慎表述不符。',
          '排除 C：缩小范围（only），文中讨论的是全行业影响。',
          '确认 B：全面概括了文章正反两面的讨论，为主旨。',
        ],
      },
      {
        number: 2,
        questionType: '细节题',
        content: 'According to the passage, critics of AI are primarily concerned about:',
        options: {
          A: 'The high cost of implementing AI systems.',
          B: 'The potential loss of jobs for workers doing repetitive tasks.',
          C: 'The lack of intelligence in current AI systems.',
          D: 'The slow pace of AI development.',
        },
        correctAnswer: 'B',
        analysis: {
          A: {
            trapType: '无中生有',
            explanation: '文中未提及 AI 实施成本（high cost），属于无中生有。',
          },
          B: {
            trapType: '正确',
            explanation:
              '原文定位：Critics warn that ... lead to widespread job displacement, particularly among workers whose roles involve routine, repetitive tasks。',
          },
          C: {
            trapType: '无中生有',
            explanation: '文中未提及 AI 缺乏智能（lack of intelligence），属于无中生有。',
          },
          D: {
            trapType: '正反混淆',
            explanation:
              '文中说 rapid deployment（快速部署），选项说 slow pace（缓慢步伐），意思相反。',
          },
        },
        steps: [
          '识别题型：细节题，需要定位原文具体信息。',
          '定位关键词 critics → 原文第二句 Critics, however, warn that ...',
          '排除 A、C：文中未提及成本和 AI 智能不足，无中生有。',
          '排除 D：原文说 rapid（快速），选项说 slow（缓慢），正反混淆。',
          '确认 B：与原文 job displacement + repetitive tasks 完全对应。',
        ],
      },
    ],
  },
  {
    id: '2023_en1_t1',
    year: 2023,
    examType: '英语一',
    textNumber: 1,
    passage:
      'Climate change has emerged as one of the most pressing challenges of our time, demanding coordinated action from governments, corporations, and individuals alike. While some progress has been made in reducing carbon emissions in certain sectors, the overall trajectory remains concerning. Scientists warn that without immediate and sustained intervention, global temperatures could rise by as much as 3 degrees Celsius above pre-industrial levels by the end of this century. The consequences of such warming, which include more frequent extreme weather events, rising sea levels, and disruptions to agricultural systems, would be felt disproportionately by vulnerable populations in developing nations.',
    questions: [
      {
        number: 1,
        questionType: '推理题',
        content: 'It can be inferred from the passage that:',
        options: {
          A: 'Current efforts to reduce carbon emissions have been entirely sufficient.',
          B: 'Developing nations are more likely to suffer from the effects of climate change.',
          C: 'Global temperatures have already risen by 3 degrees Celsius.',
          D: 'Individuals play no role in addressing climate change.',
        },
        correctAnswer: 'B',
        analysis: {
          A: {
            trapType: '正反混淆',
            explanation:
              '文中说 the overall trajectory remains concerning（总体趋势令人担忧），选项说 entirely sufficient（完全足够），意思相反。',
          },
          B: {
            trapType: '正确',
            explanation:
              '推理依据：末句说 consequences ... would be felt disproportionately by vulnerable populations in developing nations，可推出发展中国家更可能受影响。',
          },
          C: {
            trapType: '偷换概念',
            explanation:
              '文中说 could rise by as much as 3 degrees（可能上升多达 3 度），选项说 have already risen（已经上升），将未来可能变为已发生。',
          },
          D: {
            trapType: '正反混淆',
            explanation:
              '文中说 demanding coordinated action from ... individuals alike（需要个人共同行动），选项说 individuals play no role（个人不起作用），意思相反。',
          },
        },
        steps: [
          '识别题型：推理题，需要从文中信息合理推断。',
          '定位末句：consequences would be felt disproportionately by vulnerable populations in developing nations。',
          '排除 A：原文说 trajectory remains concerning，与 sufficient 矛盾。',
          '排除 C：原文说 could rise（可能上升），选项说 already risen（已上升），偷换时态。',
          '排除 D：原文说需要 individuals 行动，与 no role 矛盾。',
          '确认 B：从 disproportionately（不成比例地）可推出发展中国家受影响更大。',
        ],
      },
    ],
  },
]

const questionMeta: Record<
  string,
  { location: string; sourceSentence: string; sourceHighlights: string[] }
> = {
  '2024_en1_t1-q1': {
    location: '全文 · 首段总起 + 第三句转折',
    sourceSentence:
      'The rise of artificial intelligence has prompted both excitement and anxiety in equal measure.',
    sourceHighlights: ['both excitement and anxiety', 'in equal measure'],
  },
  '2024_en1_t1-q2': {
    location: '第一段 · 第 3 句（Critics, however ...）',
    sourceSentence:
      'Critics, however, warn that the rapid deployment of AI systems could lead to widespread job displacement, particularly among workers whose roles involve routine, repetitive tasks.',
    sourceHighlights: ['Critics', 'job displacement', 'routine, repetitive tasks'],
  },
  '2023_en1_t1-q1': {
    location: '第一段 · 末句（The consequences ...）',
    sourceSentence:
      'The consequences of such warming, which include more frequent extreme weather events, rising sea levels, and disruptions to agricultural systems, would be felt disproportionately by vulnerable populations in developing nations.',
    sourceHighlights: [
      'disproportionately',
      'vulnerable populations',
      'developing nations',
    ],
  },
}

export const questions: Question[] = passages.flatMap((passage) =>
  passage.questions.map((question) => {
    const id = `${passage.id}-q${question.number}`
    const meta = questionMeta[id]
    return {
      ...question,
      id,
      passageId: passage.id,
      year: passage.year,
      examType: passage.examType,
      textNumber: passage.textNumber,
      location: meta.location,
      sourceSentence: meta.sourceSentence,
      sourceHighlights: meta.sourceHighlights,
    }
  }),
)

export const getPassage = (id: string) => passages.find((item) => item.id === id)

export const QUESTION_TYPES: {
  name: QuestionType
  desc: string
  signal: string
  steps: string[]
}[] = [
  {
    name: '细节题',
    desc: '定位原文具体信息，找同义替换。',
    signal: 'according to / based on / the passage states',
    steps: ['圈定题干关键词', '回原文精确定位', '比对同义替换，排除无据选项'],
  },
  {
    name: '主旨题',
    desc: '概括全文或段落核心观点。',
    signal: 'main idea / mainly about / best title',
    steps: ['读首尾段与转折句', '归纳作者核心态度', '排除局部信息与过宽选项'],
  },
  {
    name: '推理题',
    desc: '从文中信息合理推断，不过度推理。',
    signal: 'infer / imply / suggest / can be concluded',
    steps: ['定位推理依据句', '区分“文中明说”与“合理推出”', '排除绝对化与无据延伸'],
  },
  {
    name: '词义题',
    desc: '根据上下文推断词或短语含义。',
    signal: 'means / refers to / closest in meaning',
    steps: ['回原文找指代范围', '利用并列、转折、解释结构', '代入原句验证逻辑'],
  },
  {
    name: '态度题',
    desc: '判断作者对某事物的态度。',
    signal: 'attitude / tone / author feels',
    steps: ['找评价性形容词与副词', '区分作者与文中他人态度', '排除中立项与过度情绪项'],
  },
]

export const TRAP_TYPES: {
  name: string
  desc: string
  signal: string
  tone: Tone
}[] = [
  {
    name: '偷换概念',
    desc: '将文中的某个词或概念替换为相近但不同的说法。',
    signal: '时态偷换 / 主体偷换 / 程度偷换',
    tone: 'red',
  },
  {
    name: '扩大范围',
    desc: '将文中的局部、有限范围扩大为全部、普遍。',
    signal: 'all / every / always / 全行业',
    tone: 'amber',
  },
  {
    name: '缩小范围',
    desc: '将文中的普遍范围缩小为局部或有限对象。',
    signal: 'only / merely / just',
    tone: 'amber',
  },
  {
    name: '正反混淆',
    desc: '将文中的肯定变否定，或把意思说反。',
    signal: 'not / never / fail to / 与原文相反',
    tone: 'red',
  },
  {
    name: '无中生有',
    desc: '选项信息在原文中完全没有依据。',
    signal: '原文未出现的名词、数据、比较关系',
    tone: 'cyan',
  },
  {
    name: '过于绝对',
    desc: '将文中的可能、有时变为必然、总是。',
    signal: 'definitely / must / never / entirely',
    tone: 'red',
  },
  {
    name: '过度推理',
    desc: '从原文信息推出超出作者表达范围的结论。',
    signal: '必然导致 / 完全说明 / 由此证明',
    tone: 'violet',
  },
  {
    name: '张冠李戴',
    desc: '把文中 A 的观点、行为或特征安到 B 身上。',
    signal: '主体错位 / 观点归属错误',
    tone: 'violet',
  },
]

export const METHODOLOGY: {
  name: string
  desc: string
  steps: string[]
}[] = [
  {
    name: '长难句拆解五步法',
    desc: '先结构，后意思。把复杂句拆到能复述为止。',
    steps: [
      '找主干：主语 + 谓语 + 宾语，先回答“谁做了什么”。',
      '剥离从句：识别 that / which / who / whose / because 等引导词。',
      '划分修饰：介词短语、分词短语、形容词短语逐一归位。',
      '逐层翻译：先主干后修饰，按中文语序重新组装。',
      '标注语法点：从句类型、特殊结构、虚拟语气与倒装。',
    ],
  },
  {
    name: '选项分析五步法',
    desc: '先定位，再辨型，最后用陷阱类型排除。',
    steps: [
      '定位原文：根据题干关键词找到对应句或段落。',
      '识别题型：细节、主旨、推理、词义、态度五类。',
      '分析陷阱：逐项对照原文，标注陷阱类型。',
      '排除干扰：先排除绝对项、无据项、反义项。',
      '确认答案：剩余选项回原文核对同义替换。',
    ],
  },
]

const sentence2024: string[] = [
  'The rise of artificial intelligence has prompted both excitement and anxiety in equal measure.',
  'Proponents argue that AI will revolutionize industries, streamline processes, and create new categories of jobs that we cannot yet imagine.',
  'Critics, however, warn that the rapid deployment of AI systems could lead to widespread job displacement, particularly among workers whose roles involve routine, repetitive tasks.',
  'What remains clear is that the technology which once seemed confined to the realm of science fiction has now become an inescapable part of our daily lives, raising questions about privacy, accountability, and the very definition of human capability.',
]

export const SENTENCE_ANALYSES: SentenceAnalysis[] = [
  {
    id: 's1',
    index: 1,
    source: '2024 英语一 · Text 1 · 第 1 句',
    original: sentence2024[0],
    isLong: false,
    segments: [
      { text: 'The rise of artificial intelligence', tone: 'blue', label: '主语 + 后置定语' },
      { text: ' has prompted ', tone: 'slate' },
      { text: 'both excitement and anxiety', tone: 'emerald', label: '并列宾语' },
      { text: ' in equal measure', tone: 'amber', label: '程度状语' },
      { text: '.', tone: 'slate' },
    ],
    main: 'The rise of artificial intelligence has prompted both excitement and anxiety.',
    mainNote:
      '主语中心词是 rise，of artificial intelligence 作后置定语；谓语 has prompted 使用现在完成时；宾语由 both ... and ... 并列。',
    clauses: [],
    clauseNote: '本句没有从句，是标准的简单句。能判断“没有从句”，同样是长难句训练的基本功。',
    modifiers: [
      {
        label: '后置定语',
        text: 'of artificial intelligence',
        note: '修饰 rise，说明是哪一种兴起。',
      },
      {
        label: '程度状语',
        text: 'in equal measure',
        note: '修饰 prompted，表示“同等程度地”。',
      },
    ],
    translation: '人工智能的兴起，同等程度地引发了兴奋与焦虑。',
    translationLayers: [
      '人工智能的兴起',
      '同等程度地引发了',
      '兴奋与焦虑',
    ],
    grammar: [
      { name: '介词短语作后置定语', note: 'of artificial intelligence 修饰 rise。' },
      { name: 'both ... and ... 并列', note: '连接 excitement 与 anxiety。' },
      { name: '现在完成时', note: 'has prompted 强调影响延续至今。' },
    ],
    examPoints: [
      '首句常常是主旨题的定位句，both ... and ... 提示作者要讨论正反两面。',
      'in equal measure 意为“同等程度地”，不要译成“公平地”。',
    ],
    tree: [
      {
        label: 'The rise ... has prompted ...',
        role: '主干 · 主谓宾',
        children: [
          { label: 'The rise', role: '主语' },
          { label: 'of artificial intelligence', role: '后置定语' },
          { label: 'has prompted', role: '谓语 · 现在完成时' },
          { label: 'both excitement and anxiety', role: '并列宾语' },
          { label: 'in equal measure', role: '程度状语' },
        ],
      },
    ],
  },
  {
    id: 's2',
    index: 2,
    source: '2024 英语一 · Text 1 · 第 2 句',
    original: sentence2024[1],
    isLong: true,
    segments: [
      { text: 'Proponents argue', tone: 'blue', label: '主干' },
      {
        text: ' that AI will revolutionize industries, streamline processes, and create new categories of jobs',
        tone: 'violet',
        label: '宾语从句',
      },
      { text: ' that we cannot yet imagine', tone: 'amber', label: '定语从句' },
      { text: '.', tone: 'slate' },
    ],
    main: 'Proponents argue that AI will revolutionize industries, streamline processes, and create new categories of jobs.',
    mainNote:
      '主语 Proponents，谓语 argue；that 从句整体作宾语。从句内部三个动词并列，共享情态动词 will。',
    clauses: [
      {
        label: '宾语从句',
        text: 'that AI will revolutionize industries, streamline processes, and create new categories of jobs',
        note: 'that 引导，作 argue 的宾语。',
      },
      {
        label: '定语从句',
        text: 'that we cannot yet imagine',
        note: '修饰 jobs，that 在从句中作 imagine 的宾语。',
      },
    ],
    clauseNote: '两个 that 连续出现，第一个引导宾语从句，第二个引导定语从句。',
    modifiers: [
      {
        label: '并列谓语',
        text: 'revolutionize ..., streamline ..., and create ...',
        note: '三个动词共享 will，构成排比。',
      },
      {
        label: '介词短语',
        text: 'of jobs',
        note: '修饰 categories，说明是“工作”的新类别。',
      },
    ],
    translation:
      '支持者认为，人工智能将颠覆各个行业、简化流程，并创造出我们目前还无法想象的新工作类别。',
    translationLayers: [
      '支持者认为',
      '人工智能将颠覆行业、简化流程',
      '并创造新的工作类别',
      '这些工作是我们目前还无法想象的',
    ],
    grammar: [
      { name: '宾语从句', note: 'that 引导，作 argue 的宾语。' },
      { name: '定语从句', note: 'that 引导，修饰 jobs。' },
      { name: '并列谓语', note: 'revolutionize / streamline / create 三项并列。' },
    ],
    examPoints: [
      'that 连续出现时，先判断它是否在从句中充当成分，再确定从句类型。',
      'cannot yet imagine 中的 yet 表示“尚不能”，是推理题常见的改写点。',
    ],
    tree: [
      {
        label: 'Proponents argue',
        role: '主干 · 主谓',
        children: [
          { label: 'Proponents', role: '主语' },
          { label: 'argue', role: '谓语' },
          {
            label: 'that AI will revolutionize ...',
            role: '宾语从句',
            children: [
              { label: 'AI', role: '从句主语' },
              { label: 'will revolutionize / streamline / create', role: '并列谓语' },
              { label: 'that we cannot yet imagine', role: '定语从句 → jobs' },
            ],
          },
        ],
      },
    ],
  },
  {
    id: 's3',
    index: 3,
    source: '2024 英语一 · Text 1 · 第 3 句',
    original: sentence2024[2],
    isLong: true,
    segments: [
      { text: 'Critics, however, warn', tone: 'blue', label: '主干 + 插入语' },
      {
        text: ' that the rapid deployment of AI systems could lead to widespread job displacement',
        tone: 'violet',
        label: '宾语从句',
      },
      { text: ' particularly among workers', tone: 'amber', label: '状语' },
      {
        text: ' whose roles involve routine, repetitive tasks',
        tone: 'cyan',
        label: '定语从句',
      },
      { text: '.', tone: 'slate' },
    ],
    main: 'Critics warn that the rapid deployment of AI systems could lead to widespread job displacement.',
    mainNote:
      '主语 Critics，插入语 however 不影响主干；谓语 warn；that 从句作宾语，particularly among workers 补充说明对象。',
    clauses: [
      {
        label: '宾语从句',
        text: 'that the rapid deployment of AI systems could lead to widespread job displacement',
        note: 'that 引导，作 warn 的宾语。',
      },
      {
        label: '定语从句',
        text: 'whose roles involve routine, repetitive tasks',
        note: 'whose 引导，修饰 workers；whose 在从句中作定语。',
      },
    ],
    clauseNote: '宾语从句里再套一个 whose 定语从句，是典型的“从句嵌套”。',
    modifiers: [
      {
        label: '插入语',
        text: 'however',
        note: '表示转折，连接上一句支持者的乐观论调。',
      },
      {
        label: '介词短语',
        text: 'of AI systems',
        note: '修饰 deployment，说明部署的对象。',
      },
      {
        label: '介词短语',
        text: 'among workers',
        note: '限定 job displacement 波及的人群。',
      },
      {
        label: '并列形容词',
        text: 'routine, repetitive',
        note: '共同修饰 tasks。',
      },
    ],
    translation:
      '然而，批评者警告说，人工智能系统的快速部署可能导致大范围岗位流失，尤其是那些工作内容涉及例行、重复性任务的劳动者。',
    translationLayers: [
      '然而，批评者警告说',
      '人工智能系统的快速部署',
      '可能导致大范围岗位流失',
      '尤其是那些从事例行、重复性工作的劳动者',
    ],
    grammar: [
      { name: '宾语从句', note: 'that 引导，作 warn 的宾语。' },
      { name: 'whose 定语从句', note: '修饰 workers，whose 作定语。' },
      { name: '插入语', note: 'however 表示转折。' },
    ],
    examPoints: [
      'whose 引导定语从句时，先行词是人或物，whose 在从句中作定语。',
      'particularly among ... 是细节题定位的高频信号，注意“尤其”后面的对象。',
    ],
    tree: [
      {
        label: 'Critics ... warn',
        role: '主干 · 主谓',
        children: [
          { label: 'Critics', role: '主语' },
          { label: 'however', role: '插入语 · 转折' },
          { label: 'warn', role: '谓语' },
          {
            label: 'that the rapid deployment ... could lead to ...',
            role: '宾语从句',
            children: [
              { label: 'the rapid deployment of AI systems', role: '从句主语' },
              { label: 'could lead to', role: '从句谓语' },
              { label: 'widespread job displacement', role: '从句宾语' },
              { label: 'particularly among workers', role: '状语' },
              { label: 'whose roles involve ...', role: '定语从句 → workers' },
            ],
          },
        ],
      },
    ],
  },
  {
    id: 's4',
    index: 4,
    source: '2024 英语一 · Text 1 · 第 4 句',
    original: sentence2024[3],
    isLong: true,
    segments: [
      { text: 'What remains clear', tone: 'blue', label: '主语从句' },
      { text: ' is ', tone: 'slate' },
      { text: 'that the technology', tone: 'violet', label: '表语从句' },
      {
        text: ' which once seemed confined to the realm of science fiction',
        tone: 'amber',
        label: '定语从句',
      },
      {
        text: ' has now become an inescapable part of our daily lives',
        tone: 'emerald',
        label: '表语从句主干',
      },
      {
        text: ', raising questions about privacy, accountability, and the very definition of human capability',
        tone: 'cyan',
        label: '伴随状语',
      },
      { text: '.', tone: 'slate' },
    ],
    main:
      'What remains clear is that the technology has now become an inescapable part.',
    mainNote:
      'What remains clear 是主语从句作主语，is 是系动词，that 引导表语从句；which 从句嵌套在表语从句内部，修饰 technology。',
    clauses: [
      {
        label: '主语从句',
        text: 'What remains clear',
        note: 'What 引导，整个从句作主句主语。',
      },
      {
        label: '表语从句',
        text: 'that the technology ... has now become an inescapable part of our daily lives',
        note: 'that 引导，位于系动词 is 之后。',
      },
      {
        label: '定语从句',
        text: 'which once seemed confined to the realm of science fiction',
        note: 'which 引导，修饰 technology，嵌套在表语从句中。',
      },
    ],
    clauseNote: '主句、表语从句、定语从句三层嵌套，是本篇最具代表性的长难句。',
    modifiers: [
      {
        label: '介词短语',
        text: 'to the realm of science fiction',
        note: '与 confined 搭配，表示“局限于科幻小说领域”。',
      },
      {
        label: '介词短语',
        text: 'of our daily lives',
        note: '修饰 part，说明是“日常生活”的一部分。',
      },
      {
        label: '现在分词短语',
        text: 'raising questions about privacy, accountability, and the very definition of human capability',
        note: '作伴随状语，逻辑主语是前面整个事实。',
      },
    ],
    translation:
      '有一点始终明确：这项曾经似乎只存在于科幻小说领域的技术，如今已成为我们日常生活中不可回避的一部分；这也引发了关于隐私、责任以及人类能力定义的种种问题。',
    translationLayers: [
      '有一点始终明确',
      '这项技术如今已成为我们日常生活中不可回避的一部分',
      '它曾经似乎只局限于科幻小说领域',
      '这引发了对隐私、责任和人类能力定义的追问',
    ],
    grammar: [
      { name: '主语从句', note: 'What remains clear 作主句主语。' },
      { name: '表语从句', note: 'that 引导，位于 is 之后。' },
      { name: '定语从句', note: 'which 引导，修饰 technology。' },
      { name: '现在分词作伴随状语', note: 'raising 的逻辑主语是前面整个事实。' },
    ],
    examPoints: [
      '主语从句 What remains clear 是主句主语，不要把 clear 误判为谓语。',
      'which 从句嵌套在表语从句内部，是本题最容易读丢的结构。',
      'raising 的逻辑主语是前面整个事实，不是 technology。',
    ],
    tree: [
      {
        label: 'What remains clear is that ...',
        role: '主干 · 主系表',
        children: [
          { label: 'What remains clear', role: '主语从句' },
          { label: 'is', role: '系动词' },
          {
            label: 'that the technology ... has become ...',
            role: '表语从句',
            children: [
              { label: 'the technology', role: '从句主语' },
              {
                label: 'which once seemed confined ...',
                role: '定语从句 → technology',
                children: [
                  { label: 'to the realm of science fiction', role: '介词短语' },
                ],
              },
              { label: 'has now become', role: '从句谓语' },
              { label: 'an inescapable part of our daily lives', role: '从句表语' },
            ],
          },
          {
            label: 'raising questions about ...',
            role: '伴随状语',
            children: [
              { label: 'about privacy, accountability, and ...', role: '介词短语' },
            ],
          },
        ],
      },
    ],
  },
]

export interface CompareScenario {
  id: string
  title: string
  question: string
  generic: string
  genericGaps: string[]
  genericVerdict: string
  custom: { label: string; value: string | string[] }[]
}

export const COMPARISONS: CompareScenario[] = [
  {
    id: 'sentence',
    title: '长难句拆解',
    question:
      '同一句：The technology which once seemed confined to science fiction has become part of our daily lives.',
    generic:
      '直接翻译全句：“这项曾经似乎只存在于科幻小说领域的技术如今已成为我们日常生活的一部分。”翻译结束，没有结构解释。',
    genericGaps: ['没有标出主干', '没有拆出 which 定语从句', '没有解释翻译层次'],
    genericVerdict: '结论：读懂了意思，但说不出为什么这样翻。',
    custom: [
      { label: '第一步 · 找主干', value: 'The technology has become part of our daily lives.' },
      {
        label: '第二步 · 剥离从句',
        value: 'which once seemed confined to science fiction（定语从句，修饰 technology）',
      },
      {
        label: '第三步 · 划分修饰',
        value: ['to science fiction（介词短语）', 'of our daily lives（介词短语）'],
      },
      {
        label: '第四步 · 逐层翻译',
        value: '技术已成为日常生活的一部分 → 它曾经似乎只存在于科幻小说中',
      },
      {
        label: '第五步 · 语法点',
        value: ['which 定语从句', 'seem confined 系表结构', '嵌套修饰'],
      },
    ],
  },
  {
    id: 'option',
    title: '选项陷阱分析',
    question: '同一题：What is the main idea of the passage?（正确答案 B）',
    generic: '翻译完全文后说：“选 B，因为 B 符合文章意思。”没有题型、定位与干扰项解释。',
    genericGaps: ['没有识别题型', '没有回到原文定位', '没有标注 A / C / D 的陷阱'],
    genericVerdict: '结论：选对了答案，也讲不清另外三项错在哪。',
    custom: [
      { label: '题型', value: '主旨题 · 概括全文正反两面' },
      { label: '定位', value: '全文结构：首段总起 + 第二段转折 + 末句总结' },
      { label: '选项 A', value: '过于绝对（definitely → 原文 advocates argue）' },
      { label: '选项 B', value: '正确（excitement + anxiety 全面概括）' },
      { label: '选项 C', value: '缩小范围（only → 原文讨论全行业）' },
      { label: '选项 D', value: '过于绝对（all → 原文仅说 displacement）' },
    ],
  },
  {
    id: 'word',
    title: '生词管理闭环',
    question: '同一个生词：ubiquitous（2024 英语一 Text 1）',
    generic: '翻译完就结束，不判断大纲词，不记录出处，也没有后续复习安排。',
    genericGaps: ['没有判断大纲词', '没有记录真题出处', '没有安排复习节奏'],
    genericVerdict: '结论：查过这个词，但没有形成可复习的记录。',
    custom: [
      { label: '提取', value: '从阅读原文自动提取 ubiquitous' },
      { label: '判断', value: '考研大纲词 · 高频形容词' },
      { label: '加入单词本', value: '关联出处：2024 英语一 Text 1' },
      {
        label: '复习节奏',
        value: '第 1 天 → 第 2 天 → 第 4 天 → 第 7 天 → 第 15 天 → 第 30 天',
      },
      { label: '闭环', value: '次日提醒 → 标记掌握度 → 动态调整间隔' },
    ],
  },
]
