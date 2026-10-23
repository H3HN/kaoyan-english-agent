export type QuestionType = '主旨题' | '细节题' | '推理题' | '词义题' | '态度题'
export type OptionKey = 'A' | 'B' | 'C' | 'D'
export type Tone = 'blue' | 'emerald' | 'cyan' | 'amber' | 'violet' | 'red' | 'slate'

export interface TreeNode {
  label: string
  role: string
  children?: TreeNode[]
}

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
