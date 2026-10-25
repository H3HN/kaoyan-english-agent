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
    basic_meaning TEXT NOT NULL,
    rare_meaning TEXT,
    exam_frequency INTEGER NOT NULL DEFAULT 0,
    level TEXT NOT NULL DEFAULT '基础',
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
    source_note TEXT NOT NULL DEFAULT ''
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
"""


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate_schema(conn: sqlite3.Connection) -> None:
    """Add import provenance without reclassifying or rewriting legacy data.

    Sentence offsets are nullable Python string character indices into the
    passage text, using the half-open interval [char_start, char_end).
    """
    additions = {
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
        existing = {
            row[1] for row in conn.execute(f"PRAGMA table_info({table})")
        }
        for name, definition in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {definition}")


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
