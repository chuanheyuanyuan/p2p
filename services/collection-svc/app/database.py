import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'collection.db'


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS collection_cases (
                case_id TEXT PRIMARY KEY,
                loan_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                bucket TEXT NOT NULL,
                principal_due TEXT NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL,
                assigned_to TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_action TEXT,
                ptp_amount TEXT,
                ptp_due_at TEXT,
                resolved_at TEXT,
                notes TEXT
            )
            '''
        )
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS collection_actions (
                action_id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                actor TEXT NOT NULL,
                note TEXT,
                result TEXT,
                ptp_amount TEXT,
                ptp_due_at TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(case_id) REFERENCES collection_cases(case_id)
            )
            '''
        )
        conn.execute('CREATE INDEX IF NOT EXISTS idx_cases_bucket ON collection_cases(bucket)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_cases_status ON collection_cases(status)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_actions_case ON collection_actions(case_id)')


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


init_db()
