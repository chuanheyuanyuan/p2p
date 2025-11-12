import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / 'notify.db'


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS notification_templates (
                template_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                channel TEXT NOT NULL,
                body TEXT NOT NULL,
                required_vars TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            '''
        )
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS notification_tasks (
                task_id TEXT PRIMARY KEY,
                template_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                status TEXT NOT NULL,
                audience_json TEXT NOT NULL,
                variables_json TEXT NOT NULL,
                send_at TEXT,
                sent_at TEXT,
                attempts INTEGER NOT NULL,
                last_error TEXT,
                rendered_body TEXT,
                idempotency_key TEXT UNIQUE,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(template_id) REFERENCES notification_templates(template_id)
            )
            '''
        )
        conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON notification_tasks(status)')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_tasks_template ON notification_tasks(template_id)')


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


init_db()
