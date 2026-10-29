import json

from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from prompts import (
    SYSTEM_PROMPT,
    SENTENCE_PARSE_PROMPT,
    OPTION_ANALYSIS_PROMPT,
    WEAKNESS_ANALYSIS_PROMPT,
)
from sentence_parser import parse_long_sentence, parse_passage, format_parse_result
from question_analyzer import analyze_options, format_analysis_result, classify_question_type
from wordbook import add_word, extract_words_from_text, get_all_words, get_review_words
from study_record import (
    add_record, get_accuracy_by_type, get_weakness_types,
    generate_study_suggestions, get_overall_stats
)
from sample_data import SAMPLE_QUESTIONS, QUESTION_TYPES, TRAP_TYPES, METHODLOGY


def _call_llm(user_prompt, system_prompt=None):
    if not LLM_API_KEY:
        return _mock_response(user_prompt)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[LLM调用失败: {e}]\n\n" + _mock_response(user_prompt)


def _mock_response(prompt):
    if "拆解" in prompt or "长难句" in prompt or "句子" in prompt:
        return json.dumps({
            "main_clause": "The technology has become an inescapable part of our daily lives",
            "sub_clauses": ["that once seemed confined to the realm of science fiction"],
            "modifiers": ["of our daily lives", "of science fiction"],
            "translation": "这项曾经似乎只存在于科幻小说领域的技术，如今已成为我们日常生活中不可或缺的一部分",
            "grammar_points": ["定语从句（that引导）", "介词短语修饰"]
        }, ensure_ascii=False, indent=2)

    if "选项" in prompt or "分析" in prompt:
        return json.dumps({
            "question_type": "细节题",
            "location": "定位原文第二段",
            "options": {
                "A": {"trap_type": "过于绝对", "explanation": "使用了绝对化词汇，原文表述更谨慎"},
                "B": {"trap_type": "正确", "explanation": "与原文信息一致，为同义替换"},
                "C": {"trap_type": "无中生有", "explanation": "文中未提及此信息"},
                "D": {"trap_type": "正反混淆", "explanation": "与原文意思相反"}
            },
            "steps": ["定位原文第二段", "识别题型：细节题", "逐项分析陷阱", "排除A/C/D", "确认B为正确答案"]
        }, ensure_ascii=False, indent=2)

    return "（演示模式：请配置LLM_API_KEY以启用完整AI功能）"


class KaoyanAgent:
    def __init__(self):
        self.name = "考研英语智学Agent"
        self.model = LLM_MODEL if LLM_API_KEY else "演示模式(Mock)"

    def chat(self, user_input):
        response = _call_llm(user_input, SYSTEM_PROMPT)
        return response

    def analyze_passage(self, passage):
        results = parse_passage(passage)
        long_sentences = [r for r in results if r["is_long"]]

        new_words = extract_words_from_text(passage)
        added_words = []
        for w in new_words[:10]:
            success, msg = add_word(w, source="阅读文章自动提取")
            if success:
                added_words.append(w)

        return {
            "total_sentences": len(results),
            "long_sentence_count": len(long_sentences),
            "sentences": results,
            "extracted_words": added_words,
            "summary": f"共{len(results)}句，其中{len(long_sentences)}个长难句，提取{len(added_words)}个生词"
        }

    def analyze_sentence(self, sentence):
        parsed = parse_long_sentence(sentence)
        if parsed["is_long"]:
            llm_prompt = SENTENCE_PARSE_PROMPT.format(sentence=sentence)
            llm_result = _call_llm(llm_prompt, SYSTEM_PROMPT)
            parsed["llm_analysis"] = llm_result
        return parsed

    def analyze_question(self, question, passage):
        analysis = analyze_options(question, passage)
        formatted = format_analysis_result(analysis, question)
        return {
            "analysis": analysis,
            "formatted": formatted
        }

    def get_question_by_id(self, question_id):
        for q in SAMPLE_QUESTIONS:
            if q["id"] == question_id:
                return q
        return None

    def list_questions(self):
        return [
            {
                "id": q["id"],
                "year": q["year"],
                "exam_type": q["exam_type"],
                "text_number": q["text_number"],
                "question_count": len(q["questions"])
            }
            for q in SAMPLE_QUESTIONS
        ]

    def get_wordbook(self):
        from wordbook import get_wordbook_stats
        return {
            "stats": get_wordbook_stats(),
            "words": get_all_words(),
            "review_due": get_review_words()
        }

    def get_study_report(self):
        return {
            "overall": get_overall_stats(),
            "accuracy_by_type": get_accuracy_by_type(),
            "weakness_types": get_weakness_types(),
            "suggestions": generate_study_suggestions()
        }

    def get_knowledge_base_info(self):
        return {
            "question_types": QUESTION_TYPES,
            "trap_types": TRAP_TYPES,
            "methodology": METHODLOGY,
            "outline_words_count": len(__import__("sample_data").OUTLINE_WORDS),
            "sample_questions_count": len(SAMPLE_QUESTIONS)
        }

    def compare_customization(self, sentence="", question=""):
        comparison = {
            "场景1_长难句拆解": {
                "通用模型": "直接翻译全句：'这项曾经似乎只存在于科幻小说领域的技术如今已成为我们日常生活中不可或缺的一部分'",
                "定制Agent": {
                    "第一步_找主干": "The technology has become an inescapable part",
                    "第二步_剥离从句": "that once seemed confined to the realm of science fiction（定语从句，修饰technology）",
                    "第三步_划分修饰": "of our daily lives（介词短语修饰part）/ of science fiction（介词短语修饰realm）",
                    "第四步_逐层翻译": "这项技术已经成为不可或缺的一部分 → 曾经似乎局限于科幻小说领域 → 我们日常生活的",
                    "第五步_语法点": ["定语从句（that引导，修饰technology）", "介词短语修饰", "seem to do结构"]
                }
            },
            "场景2_选项分析": {
                "通用模型": "翻译后说'选B，因为符合文章意思'",
                "定制Agent": {
                    "题型": "主旨题",
                    "定位": "全文概括",
                    "选项A": "过于绝对（definitely→原文用argue）",
                    "选项B": "正确（全面概括正反两面讨论）",
                    "选项C": "缩小范围（only→原文讨论全行业）",
                    "选项D": "过于绝对（all→原文说displacement非全部取代）",
                    "解题步骤": "识别题型→分析结构→排除绝对项→排除缩小项→确认B"
                }
            },
            "场景3_生词管理": {
                "通用模型": "翻译完即结束，不做后续管理",
                "定制Agent": {
                    "提取": "自动提取生词'ubiquitous'",
                    "判断": "考研大纲词（出现在大纲词汇表中）",
                    "加入单词本": "关联真题出处：2024年英语一Text 1",
                    "安排复习": "第1次：明天 / 第2次：+2天 / 第3次：+4天 / 第4次：+7天 / 第5次：+15天",
                    "闭环": "次日推送复习提醒→标记掌握度→调整复习间隔"
                }
            }
        }
        return comparison