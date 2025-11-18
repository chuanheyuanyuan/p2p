from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Generator
import sqlite3

from .config import get_settings


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                actor_id TEXT NOT NULL,
                actor_type TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                payload TEXT,
                ip_address TEXT,
                user_agent TEXT,
                source_service TEXT,
                occurred_at TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )
            '''
        )
        try:
            conn.execute('ALTER TABLE audit_events ADD COLUMN source_service TEXT')
        except sqlite3.OperationalError:
            pass
        conn.commit()


def purge_expired_events() -> None:
    settings = get_settings()
    cutoff = datetime.utcnow() - timedelta(days=settings.retention_days)
    with get_connection() as conn:
        conn.execute(
            'DELETE FROM audit_events WHERE occurred_at < ?',
            (cutoff.isoformat(),)
        )
        conn.commit()


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    settings = get_settings()
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
