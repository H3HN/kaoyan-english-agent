import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS syllabus_vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL UNIQUE,
    phonetic TEXT NOT NULL DEFAULT '',
    basic_meaning TEXT NOT NULL,
    rare_meaning TEXT,
    exam_frequency INTEGER NOT NULL DEFAULT 0,
    level TEXT NOT NULL DEFAULT '基础',
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS exam_passages (
    id TEXT PRIMARY KEY,
    year INTEGER NOT NULL,
    exam_type TEXT NOT NULL,
    text_number INTEGER NOT NULL,
    text TEXT NOT NULL,
    publication_status TEXT NOT NULL DEFAULT 'draft',
    revision INTEGER NOT NULL DEFAULT 1,
    reviewed_by TEXT NOT NULL DEFAULT '',
    reviewed_at TEXT NOT NULL DEFAULT '',
    published_at TEXT NOT NULL DEFAULT '',
    source_note TEXT NOT NULL DEFAULT '',
    UNIQUE(year, exam_type, text_number)
);

CREATE TABLE IF NOT EXISTS exam_sentences (
    id TEXT PRIMARY KEY,
    passage_id TEXT NOT NULL REFERENCES exam_passages(id),
    year INTEGER NOT NULL,
    exam_type TEXT NOT NULL,
    text_number INTEGER NOT NULL,
    paragraph INTEGER NOT NULL DEFAULT 1,
    sentence_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    grammar_tags TEXT NOT NULL DEFAULT '[]',
    source_label TEXT NOT NULL,
    char_start INTEGER,
    char_end INTEGER
);

CREATE TABLE IF NOT EXISTS exam_questions (
    id TEXT PRIMARY KEY,
    passage_id TEXT NOT NULL REFERENCES exam_passages(id),
    year INTEGER NOT NULL,
    exam_type TEXT NOT NULL,
    text_number INTEGER NOT NULL,
    number INTEGER NOT NULL,
    question_type TEXT NOT NULL,
    content TEXT NOT NULL,
    options_json TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    analysis_json TEXT NOT NULL,
    steps_json TEXT NOT NULL,
    source_sentence_id TEXT REFERENCES exam_sentences(id),
    answer_source TEXT NOT NULL DEFAULT 'unknown',
    answer_source_note TEXT NOT NULL DEFAULT '',
    review_status TEXT NOT NULL DEFAULT 'pending',
    source_quote TEXT NOT NULL DEFAULT '',
    location_status TEXT NOT NULL DEFAULT 'unverified',
    evidence_note TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS bank_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    passage_id TEXT NOT NULL,
    revision INTEGER NOT NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    created_at TEXT NOT NULL,
    snapshot_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sentence_breakdowns (
    sentence_id TEXT PRIMARY KEY REFERENCES exam_sentences(id),
    data_json TEXT NOT NULL,
    llm_used INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS trap_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    definition TEXT NOT NULL,
    signals TEXT NOT NULL,
    example TEXT NOT NULL,
    tone TEXT NOT NULL DEFAULT 'red'
);

CREATE TABLE IF NOT EXISTS user_vocab_book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    spelling TEXT NOT NULL UNIQUE,
    phonetic TEXT NOT NULL DEFAULT '',
    meaning TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT '',
    context TEXT NOT NULL DEFAULT '',
    is_outline INTEGER NOT NULL DEFAULT 1,
    familiarity REAL NOT NULL DEFAULT 0,
    review_count INTEGER NOT NULL DEFAULT 0,
    easiness REAL NOT NULL DEFAULT 2.5,
    interval_days INTEGER NOT NULL DEFAULT 1,
    repetition INTEGER NOT NULL DEFAULT 0,
    next_review TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS practice_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT NOT NULL,
    question_type TEXT NOT NULL,
    user_answer TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    trap_type TEXT,
    agent_feedback TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow TEXT NOT NULL,
    input_json TEXT NOT NULL,
    output_json TEXT NOT NULL,
    tool_trace_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS study_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_date TEXT NOT NULL,
    task_type TEXT NOT NULL,
    title TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    target_count INTEGER NOT NULL DEFAULT 1,
    done_count INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending',
    link TEXT NOT NULL DEFAULT '',
    source_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS plan_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    exam_date TEXT NOT NULL DEFAULT '',
    daily_minutes INTEGER NOT NULL DEFAULT 60,
    target_score INTEGER NOT NULL DEFAULT 70,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def _passage_practice_count(conn: sqlite3.Connection, passage_id: str) -> int:
    if not _table_exists(conn, "practice_records"):
        return 0
    return conn.execute(
        """
        SELECT COUNT(*)
        FROM practice_records AS pr
        JOIN exam_questions AS q ON q.id = pr.question_id
        WHERE q.passage_id = ?
        """,
        (passage_id,),
    ).fetchone()[0]


def _delete_passage_tree(conn: sqlite3.Connection, passage_id: str) -> None:
    conn.execute(
        "DELETE FROM sentence_breakdowns WHERE sentence_id IN "
        "(SELECT id FROM exam_sentences WHERE passage_id = ?)",
        (passage_id,),
    )
    conn.execute("DELETE FROM exam_questions WHERE passage_id = ?", (passage_id,))
    conn.execute("DELETE FROM exam_sentences WHERE passage_id = ?", (passage_id,))
    if _table_exists(conn, "bank_events"):
        conn.execute("DELETE FROM bank_events WHERE passage_id = ?", (passage_id,))
    conn.execute("DELETE FROM exam_passages WHERE id = ?", (passage_id,))


def delete_draft_passage(conn: sqlite3.Connection, passage_id: str) -> bool:
    """Delete one draft passage and its children if it has no practice history."""
    row = conn.execute(
        "SELECT publication_status FROM exam_passages WHERE id = ?", (passage_id,)
    ).fetchone()
    if row is None:
        return False
    if row["publication_status"] != "draft":
        raise RuntimeError(f"refusing to delete non-draft passage {passage_id}")
    if _passage_practice_count(conn, passage_id):
        raise RuntimeError(
            f"cannot remove draft passage {passage_id}: "
            "practice records reference its questions"
        )
    _delete_passage_tree(conn, passage_id)
    return True


def delete_draft_slot(
    conn: sqlite3.Connection, year: int, exam_type: str, text_number: int
) -> list[str]:
    """Remove unreferenced draft passages occupying one exam slot.

    This is used by the migration and by snapshot restore. A draft with
    practice records is never removed; the caller must fail loudly instead of
    silently destroying learning history.
    """
    rows = conn.execute(
        "SELECT id FROM exam_passages "
        "WHERE year = ? AND exam_type = ? AND text_number = ? "
        "AND publication_status = 'draft'",
        (year, exam_type, text_number),
    ).fetchall()
    removed: list[str] = []
    for row in rows:
        passage_id = row["id"]
        delete_draft_passage(conn, passage_id)
        removed.append(passage_id)
    return removed


def _ensure_unique_passage_slot(conn: sqlite3.Connection) -> None:
    """Clean legacy duplicate draft passages and enforce one row per slot."""
    duplicates = conn.execute(
        """
        SELECT year, exam_type, text_number, COUNT(*) AS c
        FROM exam_passages
        GROUP BY year, exam_type, text_number
        HAVING c > 1
        """
    ).fetchall()
    for row in duplicates:
        removed = delete_draft_slot(
            conn, row["year"], row["exam_type"], row["text_number"]
        )
        if not removed:
            raise RuntimeError(
                "duplicate exam passage slot without a removable draft: "
                f"{row['year']}/{row['exam_type']}/{row['text_number']}"
            )
    remaining = conn.execute(
        """
        SELECT year, exam_type, text_number, COUNT(*) AS c
        FROM exam_passages
        GROUP BY year, exam_type, text_number
        HAVING c > 1
        """
    ).fetchall()
    if remaining:
        details = ", ".join(
            f"{row['year']}/{row['exam_type']}/{row['text_number']}"
            for row in remaining
        )
        raise RuntimeError(f"duplicate exam passage slots cannot be cleaned: {details}")
    try:
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_exam_passages_slot "
            "ON exam_passages(year, exam_type, text_number)"
        )
    except sqlite3.IntegrityError as exc:
        raise RuntimeError(
            "failed to create ux_exam_passages_slot; resolve duplicate "
            "exam passages before migrating"
        ) from exc


def migrate_schema(conn: sqlite3.Connection) -> None:
    """Add import provenance without reclassifying or rewriting legacy data.

    Sentence offsets are nullable Python string character indices into the
    passage text, using the half-open interval [char_start, char_end).
    """
    additions = {
        "syllabus_vocabulary": {
            "phonetic": "TEXT NOT NULL DEFAULT ''",
            "enabled": "INTEGER NOT NULL DEFAULT 1",
        },
        "exam_passages": {
            "publication_status": "TEXT NOT NULL DEFAULT 'draft'",
            "revision": "INTEGER NOT NULL DEFAULT 1",
            "reviewed_by": "TEXT NOT NULL DEFAULT ''",
            "reviewed_at": "TEXT NOT NULL DEFAULT ''",
            "published_at": "TEXT NOT NULL DEFAULT ''",
            "source_note": "TEXT NOT NULL DEFAULT ''",
        },
        "exam_sentences": {
            "char_start": "INTEGER",
            "char_end": "INTEGER",
        },
        "exam_questions": {
            "answer_source": "TEXT NOT NULL DEFAULT 'unknown'",
            "answer_source_note": "TEXT NOT NULL DEFAULT ''",
            "review_status": "TEXT NOT NULL DEFAULT 'pending'",
            "source_quote": "TEXT NOT NULL DEFAULT ''",
            "location_status": "TEXT NOT NULL DEFAULT 'unverified'",
            "evidence_note": "TEXT NOT NULL DEFAULT ''",
        },
    }
    for table, columns in additions.items():
        if not conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table,),
        ).fetchone():
            # Legacy fixtures may predate a table entirely; SCHEMA handles it.
            continue
        existing = {
            row[1] for row in conn.execute(f"PRAGMA table_info({table})")
        }
        for name, definition in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")
    _ensure_unique_passage_slot(conn)


def init_db() -> None:
    from seed import seed_database

    conn = connect()
    try:
        conn.executescript(SCHEMA)
        migrate_schema(conn)
        seed_database(conn)
        conn.commit()
    finally:
        conn.close()
