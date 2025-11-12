import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'loan.db'


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS loan_applications (
                loan_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                requested_amount REAL NOT NULL,
                term_days INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                decision_reason TEXT,
                score INTEGER
            )
            '''
        )
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS repayment_schedules (
                loan_id TEXT PRIMARY KEY,
                currency TEXT NOT NULL,
                original_amount TEXT NOT NULL,
                outstanding_amount TEXT NOT NULL,
                paid_amount TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_paid_at TEXT,
                FOREIGN KEY (loan_id) REFERENCES loan_applications(loan_id)
            )
            '''
        )


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


init_db()
