"""Deterministic import validation and text locations, independent of the LLM/DB.

Offsets are Python character offsets [char_start, char_end) in the stored passage.
Blank lines denote paragraphs; single PDF line breaks are treated as soft wraps.
"""
from __future__ import annotations

import re
from typing import Any

LETTERS = ("A", "B", "C", "D")
QUESTION_TYPES = {"细节题", "主旨题", "推理题", "词义题", "态度题"}


class ImportValidationError(ValueError):
    def __init__(self, issues: list[str]):
        self.issues = issues
        super().__init__("；".join(issues))


def expected_numbers(text_number: int) -> list[int]:
    if text_number not in range(1, 5):
        raise ImportValidationError(["自动导入仅支持阅读理解 Part A 的 Text 1—4（每篇五题）"])
    first = 21 + (text_number - 1) * 5
    return list(range(first, first + 5))


def parse_answer_key(value: str, numbers: list[int]) -> dict[int, str]:
    """Accept ABCDA, 21-25 ABCDA, or explicit 21:A,22:B,...; never strip junk."""
    text = value.strip().upper()
    if not text:
        return {}
    range_match = re.fullmatch(r"(\d+)\s*[-—–]\s*(\d+)\s*[:：]?\s*([ABCD\s,，;；/]+)", text)
    if range_match:
        if (int(range_match[1]), int(range_match[2])) != (numbers[0], numbers[-1]):
            raise ImportValidationError(["答案序列的题号范围与当前 Text 不一致"])
        text = range_match[3]
    if re.fullmatch(r"[ABCD\s,，;；/]+", text):
        letters = re.findall(r"[ABCD]", text)
        if len(letters) != len(numbers):
            raise ImportValidationError([f"答案序列须恰有 {len(numbers)} 个 A/B/C/D，实际 {len(letters)} 个"])
        return dict(zip(numbers, letters))
    entries = re.findall(r"(\d+)\s*[:：=.、)]\s*([ABCD])", text)
    residue = re.sub(r"\d+\s*[:：=.、)]\s*[ABCD]", "", text)
    if not entries or re.sub(r"[\s,，;；/]+", "", residue):
        raise ImportValidationError(["答案格式无效：使用 ABCDA、21-25 ABCDA 或 21:A,22:B,…"])
    mapping = {int(number): letter for number, letter in entries}
    if len(mapping) != len(entries) or set(mapping) != set(numbers):
        raise ImportValidationError(["编号答案必须覆盖当前五个原题号，且不得重复或包含其他题号"])
    return mapping


def normalize_passage(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    paragraphs = re.split(r"\n[ \t]*\n+", text)
    return "\n\n".join(re.sub(r"\s+", " ", p).strip() for p in paragraphs if p.strip())


def validate_extraction(extraction: Any, text_number: int, answer_key: str = "") -> dict[str, Any]:
    numbers = expected_numbers(text_number)
    provided = parse_answer_key(answer_key, numbers)
    issues: list[str] = []
    if not isinstance(extraction, dict):
        raise ImportValidationError(["模型返回的提取结果不是 JSON 对象"])
    raw_passage = extraction.get("passage")
    passage = normalize_passage(raw_passage) if isinstance(raw_passage, str) else ""
    if not 100 <= len(passage) <= 20000:
        issues.append("文章长度须为 100—20000 字符，不能缺失或静默截断")
    raw_questions = extraction.get("questions")
    if not isinstance(raw_questions, list):
        raise ImportValidationError(issues + ["questions 必须为列表"])
    if len(raw_questions) != 5:
        issues.append(f"当前 Text 应有五题，实际提取 {len(raw_questions)} 题")
    questions = []
    seen: set[int] = set()
    for position, raw in enumerate(raw_questions, 1):
        label = f"第 {position} 条题目"
        if not isinstance(raw, dict):
            issues.append(f"{label}不是对象")
            continue
        number = raw.get("number")
        if isinstance(number, str) and re.fullmatch(r"\d+", number.strip()):
            number = int(number)
        if type(number) is not int or number not in numbers:
            issues.append(f"{label}须保留原卷题号 {numbers[0]}—{numbers[-1]}，实际 {number!r}")
            continue
        if number in seen:
            issues.append(f"题号 {number} 重复")
        seen.add(number)
        content = raw.get("content")
        if not isinstance(content, str) or not content.strip() or len(content) > 2000:
            issues.append(f"第 {number} 题题干缺失或超过 2000 字符")
        raw_options = raw.get("options")
        options = raw_options if isinstance(raw_options, dict) else {}
        if set(options) != set(LETTERS) or any(
            not isinstance(options.get(k), str) or not options[k].strip() for k in LETTERS
        ):
            issues.append(f"第 {number} 题必须有完整且非空的 A/B/C/D 四个选项")
        correct = provided.get(number, raw.get("correct_answer"))
        correct = correct.strip().upper() if isinstance(correct, str) else ""
        if correct not in LETTERS:
            issues.append(f"第 {number} 题答案必须为单个 A/B/C/D")
        quote = raw.get("source_quote", "")
        if not isinstance(quote, str):
            issues.append(f"第 {number} 题 source_quote 必须为文本")
            quote = ""
        qtype = raw.get("question_type")
        if not isinstance(qtype, str):
            qtype = "细节题"
        questions.append({
            "number": number,
            "content": content.strip() if isinstance(content, str) else "",
            "options": {k: v.strip() for k, v in options.items() if isinstance(v, str)},
            "correct_answer": correct,
            "question_type": qtype if qtype in QUESTION_TYPES else "细节题",
            "source_quote": quote.strip(),
        })
    if seen != set(numbers):
        issues.append(f"原卷题号不完整，缺少 {sorted(set(numbers) - seen)}")
    if issues:
        raise ImportValidationError(issues)
    return {"passage": passage, "questions": sorted(questions, key=lambda q: q["number"]),
            "answer_source": "provided" if provided else "inferred"}


# Protect common abbreviations/initialisms. This is a conservative splitter, not NLP parsing.
_ABBREVIATION = re.compile(r"(?:\b(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|St|vs|e\.g|i\.e)|\b(?:[A-Za-z]\.)+[A-Za-z])\.$", re.I)
_END = re.compile(r"[.!?]+[\"'’”)]*(?=\s|$)")


def split_passage(passage: str) -> list[dict[str, Any]]:
    """Split the already-normalized passage without modifying its character offsets."""
    rows = []
    for paragraph, match in enumerate(re.finditer(r"\S(?:.*?\S)?(?=\n\n|$)", passage, re.S), 1):
        block = match.group()
        start = 0
        spans = []
        for ending in _END.finditer(block):
            end = ending.end()
            before = block[:ending.start() + 1]
            if block[ending.start()] == "." and (
                _ABBREVIATION.search(before) or re.search(r"\b[A-Z]\.$", before)
            ):
                continue
            spans.append((start, end))
            start = end
        if block[start:].strip():
            spans.append((start, len(block)))
        sentence_index = 0
        for left, right in spans:
            while left < right and block[left].isspace():
                left += 1
            while right > left and block[right - 1].isspace():
                right -= 1
            if left == right:
                continue
            sentence_index += 1
            rows.append({"paragraph": paragraph, "sentence_index": sentence_index,
                         "text": block[left:right], "char_start": match.start() + left,
                         "char_end": match.start() + right})
    return rows


def locate_quote(quote: str, passage: str, sentences: list[dict[str, Any]]) -> dict[str, Any]:
    """Only unique verbatim quotes (ignoring whitespace) can bind a sentence.

    A literal quote is evidence of text occurrence, NOT proof that it answers the question.
    Multi-sentence and repeated quotes remain unbound for human review.
    """
    result = {"source_sentence_id": None, "location_status": "pending"}
    quote = quote.strip()
    if len(quote) < 12 or len(re.findall(r"[A-Za-z]+", quote)) < 3:
        return result
    pattern = r"\s+".join(re.escape(part) for part in quote.split())
    matches = list(re.finditer(pattern, passage))
    if len(matches) != 1:
        if matches:
            result["location_status"] = "ambiguous"
        return result
    found = matches[0]
    hits = [s for s in sentences if s["char_start"] < found.end() and s["char_end"] > found.start()]
    if len(hits) == 1 and hits[0]["char_start"] <= found.start() and found.end() <= hits[0]["char_end"]:
        result.update(source_sentence_id=hits[0].get("id"), location_status="exact_quote")
    elif hits:
        result["location_status"] = "multi_sentence"
    return result
