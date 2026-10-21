import json
import os
from datetime import datetime, timedelta

from config import WORDBOOK_PATH
from sample_data import OUTLINE_WORDS

REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]


def _load_wordbook():
    if os.path.exists(WORDBOOK_PATH):
        with open(WORDBOOK_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"words": []}


def _save_wordbook(data):
    with open(WORDBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_outline_word(word):
    return word.lower().strip() in OUTLINE_WORDS


def add_word(word, source=""):
    wb = _load_wordbook()
    existing = next((w for w in wb["words"] if w["spelling"].lower() == word.lower()), None)
    if existing:
        return False, f"单词 '{word}' 已在单词本中"

    now = datetime.now().isoformat()
    new_word = {
        "spelling": word.lower().strip(),
        "is_outline": is_outline_word(word),
        "source": source,
        "add_time": now,
        "review_count": 0,
        "next_review_time": (datetime.now() + timedelta(days=1)).isoformat(),
        "familiarity": 0.0,
        "review_history": []
    }
    wb["words"].append(new_word)
    _save_wordbook(wb)
    return True, f"已添加 '{word}'（{'大纲词' if new_word['is_outline'] else '非大纲词'}），下次复习：明天"


def remove_word(word):
    wb = _load_wordbook()
    original_len = len(wb["words"])
    wb["words"] = [w for w in wb["words"] if w["spelling"].lower() != word.lower()]
    if len(wb["words"]) < original_len:
        _save_wordbook(wb)
        return True, f"已删除 '{word}'"
    return False, f"单词 '{word}' 不在单词本中"


def get_all_words():
    wb = _load_wordbook()
    return wb["words"]


def get_review_words():
    wb = _load_wordbook()
    now = datetime.now()
    due = [w for w in wb["words"] if datetime.fromisoformat(w["next_review_time"]) <= now]
    return due


def review_word(word, remembered=True):
    wb = _load_wordbook()
    word_entry = next((w for w in wb["words"] if w["spelling"].lower() == word.lower()), None)
    if not word_entry:
        return False, f"单词 '{word}' 不在单词本中"

    word_entry["review_count"] += 1
    word_entry["review_history"].append({
        "time": datetime.now().isoformat(),
        "remembered": remembered
    })

    if remembered:
        idx = min(word_entry["review_count"], len(REVIEW_INTERVALS) - 1)
        interval = REVIEW_INTERVALS[idx]
        word_entry["next_review_time"] = (datetime.now() + timedelta(days=interval)).isoformat()
        word_entry["familiarity"] = min(1.0, word_entry["familiarity"] + 0.15)
    else:
        word_entry["next_review_time"] = (datetime.now() + timedelta(days=1)).isoformat()
        word_entry["familiarity"] = max(0.0, word_entry["familiarity"] - 0.1)

    _save_wordbook(wb)
    next_date = datetime.fromisoformat(word_entry["next_review_time"]).strftime("%Y-%m-%d")
    return True, f"复习记录已更新，下次复习：{next_date}"


def extract_words_from_text(text, known_threshold=0.85):
    from sample_data import OUTLINE_WORDS
    words = set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower()))
    new_words = []
    for w in words:
        if w in OUTLINE_WORDS:
            continue
        if any(existing["spelling"].lower() == w for existing in get_all_words()):
            continue
        new_words.append(w)
    return new_words


import re


def get_wordbook_stats():
    wb = _load_wordbook()
    words = wb["words"]
    total = len(words)
    outline_count = sum(1 for w in words if w["is_outline"])
    due_count = len(get_review_words())
    avg_familiarity = sum(w["familiarity"] for w in words) / total if total > 0 else 0
    return {
        "total": total,
        "outline_count": outline_count,
        "due_count": due_count,
        "avg_familiarity": round(avg_familiarity, 2)
    }


def get_review_schedule(word):
    schedule = []
    for i, interval in enumerate(REVIEW_INTERVALS):
        date = (datetime.now() + timedelta(days=interval)).strftime("%Y-%m-%d")
        schedule.append(f"第{i+1}次：{date}（+{interval}天）")
    return schedule