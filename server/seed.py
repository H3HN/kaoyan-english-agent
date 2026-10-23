import json
import re
import sqlite3
from datetime import datetime, timedelta

from db import DATA_DIR

RARE_MEANINGS = json.loads(
    (DATA_DIR / "rare_meanings.json").read_text(encoding="utf-8")
)

SUPPLEMENTAL = {
    "informed": (
        "adj. 有知识的；见多识广的",
        "adj. 见多识广的（不是“被通知的”）",
    ),
    "school": ("n. 学校；学院；学派", "n. 学派（a school of thought）"),
    "book": ("n. 书；v. 预订", "v. 预订（book a ticket）"),
    "content": (
        "adj. 满足的；n. 内容",
        "adj. 满足的（be content with）",
    ),
    "mean": ("v. 意味着；adj. 吝啬的", "adj. 吝啬的；卑鄙的"),
    "train": ("n. 火车；v. 训练", "n. 一系列（a train of thought）"),
    # 项目内置两篇真题中出现的词，公共词库去重后仍有少量缺失
    "accountability": ("n. 问责制；责任", None),
    "inescapable": ("adj. 不可避免的；不可回避的", None),
    "artificial": ("adj. 人工的；人造的", None),
    "intelligence": ("n. 智能；智力；情报", None),
    "deployment": ("n. 部署；调度", None),
    "displacement": ("n. 取代；流失；位移", None),
    "proponent": ("n. 支持者；拥护者", None),
    "revolutionize": ("v. 彻底改变", None),
    "streamline": ("v. 简化；使效率更高", None),
    "repetitive": ("adj. 重复的", None),
    "privacy": ("n. 隐私", None),
    "capability": ("n. 能力", None),
    "sustained": ("adj. 持续的", None),
    "intervention": ("n. 干预", None),
    "vulnerable": ("adj. 脆弱的；易受影响的", None),
    "disproportionately": ("adv. 不成比例地", None),
    "disruption": ("n. 中断；扰乱", None),
    "agricultural": ("adj. 农业的", None),
    "emission": ("n. 排放", None),
    "coordinated": ("adj. 协调的", None),
    "concerning": ("adj. 令人担忧的", None),
    "widespread": ("adj. 广泛的", None),
}

CORE_WORDS = {
    "accountability",
    "advocate",
    "attribute",
    "capability",
    "concern",
    "critical",
    "definition",
    "displacement",
    "deteriorate",
    "encompass",
    "inescapable",
    "intervention",
    "perpetuate",
    "privacy",
    "proponent",
    "revolutionize",
    "scrutiny",
    "streamline",
    "sustained",
    "trajectory",
    "ubiquitous",
    "vulnerable",
    "widespread",
}

TRAP_RULES = [
    (
        "偷换概念",
        "将文中的词、时态或主体替换为相近但不同的说法。",
        "时态偷换 / 主体偷换 / 程度偷换",
        "原文：could rise by 3 degrees；选项：have already risen by 3 degrees。",
        "red",
    ),
    (
        "扩大范围",
        "将局部、有限范围扩大为全部、普遍。",
        "all / every / always / 全行业 / 所有",
        "原文：widespread job displacement；选项：replace all human workers。",
        "amber",
    ),
    (
        "缩小范围",
        "将普遍范围缩小为局部或有限对象。",
        "only / merely / just / 仅限于",
        "原文：revolutionize industries；选项：only beneficial to repetitive tasks。",
        "amber",
    ),
    (
        "正反混淆",
        "把肯定说成否定，或把原文态度说反。",
        "not / never / fail to / 与原文相反",
        "原文：trajectory remains concerning；选项：efforts are entirely sufficient。",
        "red",
    ),
    (
        "无中生有",
        "选项信息在原文中完全没有依据。",
        "原文未出现的名词、数据、比较关系",
        "原文未提成本，选项出现 the high cost of implementing AI。",
        "cyan",
    ),
    (
        "过于绝对",
        "将可能、有时变为必然、总是。",
        "definitely / must / never / entirely",
        "原文：proponents argue；选项：AI will definitely create more jobs。",
        "red",
    ),
    (
        "过度推理",
        "从原文信息推出超出作者表达范围的结论。",
        "由此可以证明 / 必然导致 / 完全说明",
        "原文只说明风险，选项直接推出“应全面禁止”。",
        "violet",
    ),
    (
        "张冠李戴",
        "把文中 A 的观点、行为或特征安到 B 身上。",
        "主体错位 / 观点归属错误",
        "原文是 critics 的担忧，选项说成 scientists 的结论。",
        "violet",
    ),
]

DEMO_WORDS = [
    (
        "ubiquitous",
        "/juːˈbɪkwɪtəs/",
        "adj. 无处不在的；普遍存在的",
        "2024 英语一 · Text 1",
        "the technology has become an inescapable part of our daily lives",
        0.75,
        3,
        2,
    ),
    (
        "trajectory",
        "/trəˈdʒektəri/",
        "n. 轨迹；发展路径",
        "2023 英语一 · Text 1",
        "the overall trajectory remains concerning",
        0.45,
        2,
        -1,
    ),
    (
        "deteriorate",
        "/dɪˈtɪəriəreɪt/",
        "v. 恶化；退化",
        "2023 英语一 · Text 1",
        "the overall trajectory remains concerning",
        0.3,
        1,
        -2,
    ),
    (
        "encompass",
        "/ɪnˈkʌmpəs/",
        "v. 包含；涵盖",
        "2024 英语一 · Text 1",
        "create new categories of jobs",
        0.6,
        2,
        4,
    ),
    (
        "scrutiny",
        "/ˈskruːtəni/",
        "n. 仔细审查；监督",
        "2024 英语一 · Text 1",
        "raising questions about privacy, accountability",
        0.2,
        1,
        -1,
    ),
    (
        "accountability",
        "/əˌkaʊntəˈbɪləti/",
        "n. 问责制；责任",
        "2024 英语一 · Text 1",
        "raising questions about privacy, accountability",
        0.85,
        4,
        7,
    ),
    (
        "perpetuate",
        "/pəˈpetʃueɪt/",
        "v. 使持续；使永久化",
        "2023 英语一 · Text 1",
        "disruptions to agricultural systems",
        0.5,
        2,
        0,
    ),
]

RECORD_PATTERN = [
    ("主旨题", [True, True, False, True, True, True]),
    ("细节题", [True, True, True, False, True]),
    ("推理题", [True, False, False, True]),
    ("词义题", [True, False, True]),
    ("态度题", [False, True]),
]

DAY_OFFSETS = [0, 0, 1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 5, 5, 5, 5, 6, 6, 6, 1]


def _iso(days: float) -> str:
    return (datetime.now() + timedelta(days=days)).isoformat(timespec="seconds")


def _seed_vocabulary(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM syllabus_vocabulary").fetchone()[0]
    if count > 0:
        return

    rows = []
    path = DATA_DIR / "kaoyan_vocab.txt"
    for line in path.read_text(encoding="utf-8").splitlines():
        if "\t" not in line:
            continue
        word, meaning = line.split("\t", 1)
        word = word.strip().lower()
        meaning = " ".join(meaning.split())
        if not re.fullmatch(r"[a-z][a-z'\-]*", word):
            continue
        if word in RARE_MEANINGS:
            level = "核心"
        elif word in CORE_WORDS:
            level = "核心"
        elif len(word) >= 10:
            level = "拔高"
        else:
            level = "基础"
        rows.append(
            (
                word,
                meaning,
                RARE_MEANINGS.get(word),
                0,
                level,
            )
        )

    # 补充词库中缺失、但考研熟词僻义常考的少量词条
    existing = {row[0] for row in rows}
    for word, (basic, rare) in SUPPLEMENTAL.items():
        if word not in existing:
            rows.append((word, basic, rare, 0, "核心"))

    conn.executemany(
        """
        INSERT OR IGNORE INTO syllabus_vocabulary
            (word, basic_meaning, rare_meaning, exam_frequency, level)
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )


def _seed_exams(conn: sqlite3.Connection) -> None:
    path = DATA_DIR / "exam_slices.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    conn.executemany(
        """
        INSERT OR REPLACE INTO exam_passages (id, year, exam_type, text_number, text)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (item["id"], item["year"], item["exam_type"], item["text_number"], item["text"])
            for item in data["passages"]
        ],
    )
    conn.executemany(
        """
        INSERT OR REPLACE INTO exam_sentences
            (id, passage_id, year, exam_type, text_number, paragraph,
             sentence_index, text, grammar_tags, source_label)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item["id"],
                item["passage_id"],
                item["year"],
                item["exam_type"],
                item["text_number"],
                item["paragraph"],
                item["sentence_index"],
                item["text"],
                json.dumps(item["grammar_tags"], ensure_ascii=False),
                item["source_label"],
            )
            for item in data["sentences"]
        ],
    )
    conn.executemany(
        """
        INSERT OR REPLACE INTO exam_questions
            (id, passage_id, year, exam_type, text_number, number,
             question_type, content, options_json, correct_answer,
             analysis_json, steps_json, source_sentence_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                item["id"],
                item["passage_id"],
                item["year"],
                item["exam_type"],
                item["text_number"],
                item["number"],
                item["question_type"],
                item["content"],
                json.dumps(item["options"], ensure_ascii=False),
                item["correct_answer"],
                json.dumps(item["analysis"], ensure_ascii=False),
                json.dumps(item["steps"], ensure_ascii=False),
                item["source_sentence_id"],
            )
            for item in data["questions"]
        ],
    )


def _count_frequencies(conn: sqlite3.Connection) -> None:
    text = " ".join(
        row[0]
        for row in conn.execute("SELECT text FROM exam_sentences").fetchall()
    ).lower()
    tokens = re.findall(r"[a-z][a-z'\-]*", text)
    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1

    updates = [
        (count, word)
        for word, count in counts.items()
        if conn.execute(
            "SELECT 1 FROM syllabus_vocabulary WHERE word = ?", (word,)
        ).fetchone()
    ]
    conn.executemany(
        "UPDATE syllabus_vocabulary SET exam_frequency = ? WHERE word = ?",
        updates,
    )


def _seed_traps(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM trap_rules").fetchone()[0]
    if count > 0:
        return
    conn.executemany(
        """
        INSERT INTO trap_rules (name, definition, signals, example, tone)
        VALUES (?, ?, ?, ?, ?)
        """,
        TRAP_RULES,
    )


def _seed_demo_state(conn: sqlite3.Connection) -> None:
    word_count = conn.execute("SELECT COUNT(*) FROM user_vocab_book").fetchone()[0]
    if word_count == 0:
        rows = []
        for spelling, phonetic, meaning, source, context, familiarity, reviews, days in DEMO_WORDS:
            next_review = _iso(days)
            rows.append(
                (
                    spelling,
                    phonetic,
                    meaning,
                    source,
                    context,
                    1,
                    familiarity,
                    reviews,
                    2.5,
                    max(1, days if days > 0 else 1),
                    reviews,
                    next_review,
                )
            )
        conn.executemany(
            """
            INSERT OR IGNORE INTO user_vocab_book
                (spelling, phonetic, meaning, source, context, is_outline,
                 familiarity, review_count, easiness, interval_days, repetition,
                 next_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

    record_count = conn.execute("SELECT COUNT(*) FROM practice_records").fetchone()[0]
    if record_count > 0:
        return

    flat = []
    for question_type, results in RECORD_PATTERN:
        for result in results:
            flat.append((question_type, result))

    rows = []
    for index, (question_type, is_correct) in enumerate(flat):
        created = (
            datetime.now()
            - timedelta(days=DAY_OFFSETS[index])
            - timedelta(minutes=(index % 9) * 37)
        ).isoformat(timespec="seconds")
        rows.append(
            (
                f"seed-q{index + 1}",
                question_type,
                "B" if is_correct else ("A" if index % 2 == 0 else "C"),
                "B",
                1 if is_correct else 0,
                None if is_correct else ("无中生有" if index % 2 == 0 else "正反混淆"),
                None,
                created,
            )
        )
    conn.executemany(
        """
        INSERT INTO practice_records
            (question_id, question_type, user_answer, correct_answer, is_correct,
             trap_type, agent_feedback, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )


def seed_database(conn: sqlite3.Connection) -> None:
    _seed_vocabulary(conn)
    _seed_exams(conn)
    _count_frequencies(conn)
    _seed_traps(conn)
    _seed_demo_state(conn)
