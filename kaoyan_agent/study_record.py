import json
import os
from datetime import datetime

from config import STUDY_RECORD_PATH


def _load_records():
    if os.path.exists(STUDY_RECORD_PATH):
        with open(STUDY_RECORD_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"records": []}


def _save_records(data):
    with open(STUDY_RECORD_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_record(question_id, question_type, user_answer, correct_answer, passage_id=""):
    records = _load_records()
    is_correct = user_answer == correct_answer
    record = {
        "id": f"r{len(records['records']) + 1}",
        "question_id": question_id,
        "passage_id": passage_id,
        "question_type": question_type,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "time": datetime.now().isoformat()
    }
    records["records"].append(record)
    _save_records(records)
    return record


def get_all_records():
    return _load_records()["records"]


def get_accuracy_by_type():
    records = get_all_records()
    if not records:
        return {}

    stats = {}
    for r in records:
        qtype = r["question_type"]
        if qtype not in stats:
            stats[qtype] = {"total": 0, "correct": 0}
        stats[qtype]["total"] += 1
        if r["is_correct"]:
            stats[qtype]["correct"] += 1

    result = {}
    for qtype, s in stats.items():
        result[qtype] = {
            "total": s["total"],
            "correct": s["correct"],
            "accuracy": round(s["correct"] / s["total"], 2)
        }
    return result


def get_weakness_types(threshold=0.7):
    accuracy = get_accuracy_by_type()
    weak = []
    for qtype, info in accuracy.items():
        if info["accuracy"] < threshold:
            weak.append((qtype, info["accuracy"]))
    weak.sort(key=lambda x: x[1])
    return weak


def get_overall_stats():
    records = get_all_records()
    if not records:
        return {"total": 0, "correct": 0, "accuracy": 0}

    total = len(records)
    correct = sum(1 for r in records if r["is_correct"])
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 2)
    }


def generate_study_suggestions():
    accuracy = get_accuracy_by_type()
    weak_types = get_weakness_types()
    suggestions = []

    if not accuracy:
        suggestions.append("暂无练习记录，建议先做1-2套真题熟悉题型")
        return suggestions

    if weak_types:
        for qtype, acc in weak_types:
            suggestions.append(f"薄弱题型「{qtype}」正确率仅{acc*100:.0f}%，建议专项训练")
            suggestions.append(f"  → 推荐：从真题库中筛选{qtype}，每日练习3-5道")
    else:
        suggestions.append("各题型正确率均达标，建议保持练习频率")
        suggestions.append("可尝试限时训练，提升做题速度")

    overall = get_overall_stats()
    if overall["total"] < 20:
        suggestions.append(f"已练习{overall['total']}题，建议累计练习50题以上再做薄弱分析")

    from wordbook import get_wordbook_stats
    wb_stats = get_wordbook_stats()
    if wb_stats["due_count"] > 0:
        suggestions.append(f"有{wb_stats['due_count']}个单词待复习，建议先完成单词复习")

    return suggestions


def get_recent_records(n=10):
    records = get_all_records()
    return records[-n:] if len(records) > n else records