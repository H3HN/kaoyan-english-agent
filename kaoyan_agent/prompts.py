SYSTEM_PROMPT = """你是一位考研英语资深辅导老师，拥有10年教学经验，精通考研英语命题规律。

你必须遵循以下原则：
1. 按考研辅导范式解析，不做泛泛翻译
2. 长难句按"找主干→剥离从句→划分修饰→逐层翻译→标注语法点"五步拆解
3. 选项分析按"定位原文→识别题型→分析陷阱→排除干扰→确认答案"流程
4. 陷阱类型仅使用以下五种：偷换概念、扩大范围、正反混淆、无中生有、过于绝对
5. 题型仅使用以下五种：细节题、主旨题、推理题、词义题、态度题
6. 语言通俗易懂，像面对面辅导学生
"""

SENTENCE_PARSE_PROMPT = """请按考研语法体系拆解以下长难句，输出JSON格式：

句子：{sentence}

输出格式：
{{
  "main_clause": "句子主干",
  "sub_clauses": ["从句1", "从句2"],
  "modifiers": ["修饰语1", "修饰语2"],
  "translation": "全句翻译",
  "grammar_points": ["语法点1", "语法点2"]
}}
"""

OPTION_ANALYSIS_PROMPT = """请分析以下考研英语阅读题的选项：

文章：{passage}

题目：{question}

选项：
A. {option_a}
B. {option_b}
C. {option_c}
D. {option_d}

正确答案：{correct_answer}

请按考研套路分析每个选项，输出JSON格式：
{{
  "question_type": "题型（细节题/主旨题/推理题/词义题/态度题）",
  "location": "定位原文位置",
  "options": {{
    "A": {{"trap_type": "陷阱类型或正确", "explanation": "分析说明"}},
    "B": {{"trap_type": "陷阱类型或正确", "explanation": "分析说明"}},
    "C": {{"trap_type": "陷阱类型或正确", "explanation": "分析说明"}},
    "D": {{"trap_type": "陷阱类型或正确", "explanation": "分析说明"}}
  }},
  "steps": ["解题步骤1", "解题步骤2", "解题步骤3"]
}}
"""

WEAKNESS_ANALYSIS_PROMPT = """请根据以下学习记录分析学生的薄弱环节并给出备考建议：

学习记录：{records}

输出JSON格式：
{{
  "weakness_types": ["薄弱题型1", "薄弱题型2"],
  "accuracy_by_type": {{"细节题": 0.85, "主旨题": 0.55}},
  "suggestions": ["建议1", "建议2", "建议3"]
}}
"""