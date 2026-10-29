import re
import sqlite3
from typing import Any

from llm import analyze_paragraph
from tools import check_syllabus_vocab

from ..canvas import _canvas_action
from ..text import _sentence_parts
from .sentence import _ad_hoc_sentence

def _paragraph_insight(conn: sqlite3.Connection, text: str) -> dict[str, Any]:
    sentences = _sentence_parts(text)
    if len(sentences) <= 1:
        return _ad_hoc_sentence(conn, text)
    logic_markers = [
        (r"\b(however|but|yet|nevertheless|nonetheless)\b", "⚠️ 强转折", "转折后常出核心论断"),
        (r"\b(therefore|thus|consequently|hence|so)\b", "📌 结论", "结论常是主旨题定位点"),
        (r"\b(for example|for instance|such as)\b", "📌 例证", "例子服务于上一句观点"),
        (r"\b(because|since|as a result)\b", "🔗 因果", "原因是细节题高频定位"),
        (r"\b(first|second|third|finally|moreover|furthermore)\b", "➕ 递进/并列", "并列结构常对应多选题"),
        (r"\b(although|though|while|despite|in spite of)\b", "🔄 让步", "让步后往往是作者真实态度"),
    ]
    flow = []
    for index, sentence in enumerate(sentences):
        label = "承接"
        note = "继续推进段落信息"
        if index == 0:
            label = "提出话题"
            note = "段落起点"
        for pattern, marker_label, marker_note in logic_markers:
            if re.search(pattern, sentence, re.IGNORECASE):
                label = marker_label
                note = marker_note
                break
        flow.append(
            {
                "index": index + 1,
                "text": sentence,
                "translation": "",
                "logic": label,
                "logic_note": note,
                "stars": min(5, max(1, len(sentence.split()) // 12 + 1)),
            }
        )
    generated = analyze_paragraph(text)
    llm_used = bool(generated)
    if generated and generated.get("sentences"):
        flow = generated["sentences"]
        main_idea = generated.get("main_idea") or sentences[0]
        topic_sentence = generated.get("topic_sentence") or sentences[0]
        logic_flow = generated.get("logic_flow") or [
            {"from": flow[i - 1]["index"], "to": flow[i]["index"], "label": flow[i]["logic"]}
            for i in range(1, len(flow))
        ]
    else:
        main_idea = sentences[0]
        topic_sentence = sentences[0]
        logic_flow = [
            {"from": flow[i - 1]["index"], "to": flow[i]["index"], "label": flow[i]["logic"]}
            for i in range(1, len(flow))
        ]
    vocabulary, vocab_trace = check_syllabus_vocab(conn, text)
    data = {
        "paragraph_en": text,
        "source_label": "自定义段落 · 实时精读",
        "main_idea": main_idea,
        "topic_sentence": topic_sentence,
        "sentences": flow,
        "logic_flow": logic_flow,
        "vocabulary": [
            {
                "word": item["word"],
                "meaning": item.get("basic_meaning", ""),
                "rare_meaning": item.get("rare_meaning"),
                "sentence": next(
                    (sentence for sentence in sentences if item["word"].lower() in sentence.lower()),
                    "",
                ),
            }
            for item in vocabulary
            if item.get("in_syllabus")
        ][:12],
    }
    return {
        "intro": (
            "这段外源文本已经铺到左侧段落精读台。先看主旨句，再顺着句间逻辑看转折、例证和结论，"
            "最后再下钻到难句。"
        ),
        "sections": [],
        "tool_trace": [vocab_trace],
        "citations": [],
        "client_actions": [
            _canvas_action("paragraph", data, data["source_label"])
        ],
        "widgets": [],
        "llm_used": llm_used,
    }
