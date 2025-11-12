import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'payment.db'


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS disbursements (
                req_no TEXT PRIMARY KEY,
                loan_id TEXT NOT NULL,
                amount TEXT NOT NULL,
                account_json TEXT NOT NULL,
                channel TEXT NOT NULL,
                status TEXT NOT NULL,
                failure_reason TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            '''
        )
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS repayments (
                repayment_id TEXT PRIMARY KEY,
                loan_id TEXT NOT NULL,
                amount TEXT NOT NULL,
                currency TEXT NOT NULL,
                channel TEXT NOT NULL,
                txn_ref TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL,
                applied_amount TEXT NOT NULL,
                remaining_due TEXT NOT NULL,
                paid_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
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
