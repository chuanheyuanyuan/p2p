import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .config import get_settings

_settings = get_settings()
DB_PATH = _settings.data_store_path


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS daily_metrics (
                business_date TEXT PRIMARY KEY,
                currency TEXT NOT NULL,
                metrics_json TEXT NOT NULL,
                notes_json TEXT NOT NULL,
                generated_at TEXT NOT NULL
            )
            '''
        )
        conn.execute(
            'CREATE INDEX IF NOT EXISTS idx_daily_metrics_generated ON daily_metrics(generated_at)'
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
