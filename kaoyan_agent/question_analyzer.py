import re

from sample_data import QUESTION_TYPES, TRAP_TYPES

ABSOLUTE_WORDS = [
    "all", "every", "only", "must", "never", "always", "entirely",
    "completely", "totally", "absolutely", "definitely", "undoubtedly",
    "no one", "nothing", "none", "sole", "unique"
]

NEGATIVE_WORDS = [
    "not", "no", "never", "none", "nobody", "nothing", "neither",
    "nor", "without", "hardly", "scarcely", "barely"
]

TYPE_KEYWORDS = {
    "主旨题": ["main idea", "mainly about", "primarily concerned", "primarily about",
              "best title", "central idea", "main point", "passage is mainly",
              "author's primary", "the passage focuses"],
    "细节题": ["according to", "based on", "which of the following", "the passage states",
              "mentions", "described", "indicates that", "says that"],
    "推理题": ["infer", "imply", "suggest", "it can be inferred", "can be concluded",
              "most likely", "probably"],
    "词义题": ["means", "refers to", "closest in meaning", "could best be replaced",
              "the word", "the phrase"],
    "态度题": ["attitude", "tone", "author's attitude", "author feels"]
}


def classify_question_type(question_content):
    lower = question_content.lower()
    for qtype, keywords in TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in lower:
                return qtype
    return "细节题"


def detect_trap_type(option_text, passage, correct_answer, option_label):
    lower_opt = option_text.lower()
    lower_passage = passage.lower()

    for word in ABSOLUTE_WORDS:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, lower_opt):
            if not re.search(pattern, lower_passage):
                return "过于绝对", f"选项使用了绝对化词汇'{word}'，原文未使用"

    opt_negative = any(re.search(r'\b' + re.escape(neg) + r'\b', lower_opt) for neg in NEGATIVE_WORDS)
    passage_negative = any(re.search(r'\b' + re.escape(neg) + r'\b', lower_passage) for neg in NEGATIVE_WORDS)
    if opt_negative != passage_negative:
        return "正反混淆", "选项与原文的肯定/否定语气相反"

    opt_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', lower_opt))
    passage_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', lower_passage))
    unique_words = opt_words - passage_words
    common_words = opt_words & passage_words
    if len(unique_words) > len(common_words) * 0.6 and len(unique_words) > 3:
        return "无中生有", f"选项包含原文未出现的关键词：{', '.join(list(unique_words)[:3])}"

    return None, None


def analyze_options(question, passage):
    result = {
        "question_type": "",
        "location": "",
        "options_analysis": {},
        "steps": []
    }

    result["question_type"] = classify_question_type(question["content"])

    correct = question["correct_answer"]
    result["location"] = f"根据题干关键词定位原文相关段落"

    if "analysis" in question:
        for label, info in question["analysis"].items():
            result["options_analysis"][label] = {
                "trap_type": info["trap_type"],
                "explanation": info["explanation"]
            }
    else:
        for label in ["A", "B", "C", "D"]:
            if label == correct:
                result["options_analysis"][label] = {
                    "trap_type": "正确",
                    "explanation": "与原文信息一致，为正确答案"
                }
            else:
                trap, expl = detect_trap_type(
                    question["options"][label], passage, correct, label
                )
                result["options_analysis"][label] = {
                    "trap_type": trap if trap else "干扰项",
                    "explanation": expl if expl else "与原文信息不完全一致"
                }

    result["steps"] = [
        f"第一步：识别题型——{result['question_type']}，{QUESTION_TYPES.get(result['question_type'], '')}",
        f"第二步：定位原文——{result['location']}",
        "第三步：逐项分析——",
    ]
    for label, info in result["options_analysis"].items():
        result["steps"].append(
            f"  选项{label}：{info['trap_type']}（{info['explanation']}）"
        )
    result["steps"].append(f"第四步：排除干扰项，确认正确答案为{correct}")

    return result


def format_analysis_result(analysis, question):
    lines = []
    lines.append(f"题目：{question['content']}")
    lines.append(f"题型：{analysis['question_type']}")
    lines.append(f"定位：{analysis['location']}")
    lines.append("")
    lines.append("选项分析：")
    for label in ["A", "B", "C", "D"]:
        info = analysis["options_analysis"].get(label, {})
        trap = info.get("trap_type", "")
        expl = info.get("explanation", "")
        marker = "✅" if trap == "正确" else "❌"
        lines.append(f"  {marker} {label}. {question['options'].get(label, '')}")
        lines.append(f"     → {trap}：{expl}")
    lines.append("")
    lines.append("解题步骤：")
    for step in analysis["steps"]:
        lines.append(f"  {step}")
    return "\n".join(lines)