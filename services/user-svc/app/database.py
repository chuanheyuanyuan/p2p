import sqlite3
from contextlib import contextmanager
from typing import Iterator

from .config import Settings, get_settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS user_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    platform TEXT,
    app_version TEXT,
    privacy_consent INTEGER DEFAULT 0,
    location_consent INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_active_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, fingerprint)
);
CREATE INDEX IF NOT EXISTS idx_user_devices_user ON user_devices(user_id);
"""

_settings = get_settings()


def init_db() -> None:
    _settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(_settings.db_path) as conn:
        conn.executescript(SCHEMA)


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_settings.db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
