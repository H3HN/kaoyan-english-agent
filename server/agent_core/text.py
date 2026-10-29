import re

STOP_WORDS = {
    "the", "a", "an", "this", "that", "these", "those", "please", "agent",
    "explain", "analyze", "analyse", "translate", "sentence", "paragraph",
    "word", "phrase", "look", "at", "and", "or", "of", "to", "in", "is",
    "be", "it", "for", "with", "on", "as", "by", "from", "what", "how",
}

def _external_english(message: str) -> str | None:
    candidates = re.findall(
        r"[A-Za-z][A-Za-z0-9'’\-]*(?:[ \t,.;:!?\"“”‘’()\-]+[A-Za-z0-9'’\-]+){7,}",
        message,
    )
    if not candidates:
        return None
    return max(candidates, key=len).strip()


def _english_tokens(message: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z'’\-]*(?:\s+[A-Za-z][A-Za-z'’\-]*){0,4}", message)


def _word_target(message: str) -> str:
    quoted = re.findall(r"[“\"']([A-Za-z][A-Za-z\s'’\-]{0,50})[”\"']", message)
    if quoted:
        return quoted[0].strip()
    tokens = [
        token.strip()
        for token in re.findall(r"[A-Za-z][A-Za-z'’\-]*", message)
        if token.lower() not in STOP_WORDS
    ]
    if not tokens:
        return ""
    # Keep a compact phrase when the user explicitly asks about a phrase.
    if len(tokens) <= 4:
        return " ".join(tokens)
    return tokens[-1]


def _sentence_parts(text: str) -> list[str]:
    return [
        item.strip()
        for item in re.split(r"(?<=[.!?])\s+", text.strip())
        if item.strip()
    ]


def _writing_prompt(message: str) -> str:
    """Extract an explicit writing title from natural Chinese/English phrasing."""
    patterns = (
        r"(?:标题|题目|主题)\s*(?:为|是|叫|：|:)\s*[《“\"']?(.+?)(?=[》”\"']?(?:的)?(?:写作|作文|训练|练习|$)|[，。；;\n])",
        r"(?:以)\s*[《“\"']?(.+?)[》”\"']?\s*(?:为题|作为标题|为标题)",
    )
    # "标题为Love的写作训练" must capture Love, not the whole suffix.
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            value = match.group(1).strip().strip("《》\"“”'‘’")
            value = re.sub(r"\s+", " ", value).strip()
            if value:
                return value[:200]
    return ""
