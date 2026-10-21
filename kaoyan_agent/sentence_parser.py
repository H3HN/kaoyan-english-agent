import re

CLAUSE_CONNECTORS = [
    "that", "which", "who", "whom", "whose", "where", "when", "why",
    "because", "although", "though", "if", "unless", "as", "since",
    "while", "whereas", "before", "after", "until", "once", "so that"
]

COORDINATORS = ["and", "but", "or", "so", "yet", "for", "nor"]

PREPOSITIONS = [
    "in", "on", "at", "with", "by", "for", "of", "to", "from",
    "under", "over", "through", "across", "along", "behind", "between",
    "among", "about", "against", "without", "within", "beyond", "upon"
]

ABSOLUTE_WORDS = [
    "all", "every", "only", "must", "never", "always", "entirely",
    "completely", "totally", "absolutely", "definitely", "undoubtedly",
    "no one", "nothing", "none"
]

NEGATIVE_WORDS = [
    "not", "no", "never", "none", "nobody", "nothing", "neither",
    "nor", "without", "hardly", "scarcely", "barely", "rarely"
]


def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def is_long_sentence(sentence, threshold=15):
    word_count = len(sentence.split())
    has_connector = any(conn in sentence.lower().split() for conn in CLAUSE_CONNECTORS)
    return word_count >= threshold or has_connector


def find_main_clause(sentence):
    lower = sentence.lower()
    for conn in CLAUSE_CONNECTORS:
        pattern = r'\b' + re.escape(conn) + r'\b'
        match = re.search(pattern, lower)
        if match:
            return sentence[:match.start()].strip().rstrip(',').strip()
    for coord in COORDINATORS:
        pattern = r'\b' + re.escape(coord) + r'\b'
        matches = list(re.finditer(pattern, lower))
        if matches:
            mid = matches[len(matches) // 2]
            return sentence[:mid.start()].strip().rstrip(',').strip()
    return sentence


def find_sub_clauses(sentence):
    lower = sentence.lower()
    clauses = []
    for conn in CLAUSE_CONNECTORS:
        pattern = r'\b' + re.escape(conn) + r'\b'
        match = re.search(pattern, lower)
        if match:
            sub = sentence[match.start():].strip()
            for next_conn in CLAUSE_CONNECTORS:
                if next_conn != conn:
                    next_pattern = r'\b' + re.escape(next_conn) + r'\b'
                    next_match = re.search(next_pattern, sub[1:])
                    if next_match:
                        sub = sub[:next_match.start() + 1].strip()
                        break
            clauses.append(sub)
    return clauses


def find_modifiers(sentence):
    modifiers = []
    lower = sentence.lower()
    for prep in PREPOSITIONS:
        pattern = r'\b' + re.escape(prep) + r'\b'
        match = re.search(pattern, lower)
        if match:
            rest = sentence[match.start():]
            end_match = re.search(r'[,.]', rest[1:])
            if end_match:
                mod = rest[:end_match.start() + 1].strip()
            else:
                mod = rest.strip()
            if len(mod.split()) <= 8 and mod not in modifiers:
                modifiers.append(mod)

    ing_pattern = re.findall(r'\b\w+ing\b[^,;.]*', sentence)
    for ing in ing_pattern[:2]:
        if len(ing.split()) >= 2 and ing not in modifiers:
            modifiers.append(ing.strip())

    ed_pattern = re.findall(r'\b\w+ed\b[^,;.]*', sentence)
    for ed in ed_pattern[:1]:
        if len(ed.split()) >= 3 and ed not in modifiers:
            modifiers.append(ed.strip())

    return modifiers[:4]


def identify_grammar_points(sentence):
    points = []
    lower = sentence.lower()

    for conn in CLAUSE_CONNECTORS:
        if re.search(r'\b' + re.escape(conn) + r'\b', lower):
            if conn in ["that", "which", "who", "whom", "whose"]:
                points.append(f"定语从句（{conn}引导）")
            elif conn in ["where", "when"]:
                points.append(f"状语从句/定语从句（{conn}引导）")
            elif conn in ["because", "since", "as"]:
                points.append(f"原因状语从句（{conn}引导）")
            elif conn in ["although", "though"]:
                points.append(f"让步状语从句（{conn}引导）")
            elif conn in ["if", "unless"]:
                points.append(f"条件状语从句（{conn}引导）")
            elif conn in ["while", "whereas"]:
                points.append(f"对比状语从句（{conn}引导）")

    if re.search(r'\b\w+ing\b', lower):
        points.append("现在分词结构")
    if re.search(r'\b\w+ed\b', lower) and not re.search(r'\b(have|has|had)\b', lower):
        points.append("过去分词结构")
    if re.search(r'\bto \w+\b', lower):
        points.append("不定式结构")
    if re.search(r'\b(may|might|could|would|should)\b', lower):
        points.append("情态动词/虚拟语气")

    return list(dict.fromkeys(points))


def simple_translate(sentence):
    common_translations = {
        "the": "这个", "a": "一个", "an": "一个", "is": "是", "are": "是",
        "was": "是", "were": "是", "has": "有", "have": "有", "had": "有",
        "and": "和", "but": "但是", "or": "或者", "in": "在...里",
        "of": "的", "to": "到", "for": "为了", "with": "伴随",
        "that": "那", "this": "这", "which": "哪个", "who": "谁",
    }
    words = re.findall(r'\b\w+\b', sentence.lower())
    translated = []
    for w in words:
        if w in common_translations:
            translated.append(common_translations[w])
        else:
            translated.append(w)
    return " ".join(translated)


def parse_long_sentence(sentence):
    result = {
        "original": sentence,
        "is_long": is_long_sentence(sentence),
        "main_clause": "",
        "sub_clauses": [],
        "modifiers": [],
        "translation": "",
        "grammar_points": []
    }

    if not result["is_long"]:
        result["main_clause"] = sentence
        result["translation"] = simple_translate(sentence)
        return result

    result["main_clause"] = find_main_clause(sentence)
    result["sub_clauses"] = find_sub_clauses(sentence)
    result["modifiers"] = find_modifiers(sentence)
    result["grammar_points"] = identify_grammar_points(sentence)
    result["translation"] = simple_translate(sentence)

    return result


def parse_passage(passage):
    sentences = split_sentences(passage)
    results = []
    for i, sent in enumerate(sentences):
        parsed = parse_long_sentence(sent)
        parsed["index"] = i + 1
        results.append(parsed)
    return results


def format_parse_result(parsed):
    lines = []
    lines.append(f"【第{parsed['index']}句】{'⚠️长难句' if parsed['is_long'] else '✅简单句'}")
    lines.append(f"原文：{parsed['original']}")
    if parsed["is_long"]:
        lines.append(f"主干：{parsed['main_clause']}")
        if parsed["sub_clauses"]:
            lines.append("从句：")
            for sc in parsed["sub_clauses"]:
                lines.append(f"  - {sc}")
        if parsed["modifiers"]:
            lines.append("修饰：")
            for mod in parsed["modifiers"]:
                lines.append(f"  - {mod}")
        if parsed["grammar_points"]:
            lines.append(f"语法点：{', '.join(parsed['grammar_points'])}")
    lines.append(f"翻译：{parsed['translation']}")
    return "\n".join(lines)