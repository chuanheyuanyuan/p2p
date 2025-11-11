import sqlite3
from contextlib import contextmanager
from typing import Iterator

from .config import CHANNEL_DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS channel_attributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    install_id TEXT NOT NULL,
    channel TEXT NOT NULL,
    campaign TEXT,
    event TEXT NOT NULL,
    cost REAL DEFAULT 0,
    occurred_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(install_id, event)
);
CREATE INDEX IF NOT EXISTS idx_channel_attributions_event_time ON channel_attributions(event, occurred_at);
CREATE INDEX IF NOT EXISTS idx_channel_attributions_channel ON channel_attributions(channel);
"""


def init_db() -> None:
    CHANNEL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(CHANNEL_DB_PATH) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(CHANNEL_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
