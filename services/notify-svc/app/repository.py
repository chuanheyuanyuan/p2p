import json
from datetime import datetime
from typing import List, Optional

from .database import get_connection
from .models import NotificationTask, NotificationTemplate


def save_template(template: NotificationTemplate) -> NotificationTemplate:
    template.updated_at = datetime.utcnow()
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO notification_templates (
                template_id, name, channel, body, required_vars,
                description, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(template_id) DO UPDATE SET
                name=excluded.name,
                channel=excluded.channel,
                body=excluded.body,
                required_vars=excluded.required_vars,
                description=excluded.description,
                updated_at=excluded.updated_at
            ''',
            (
                template.template_id,
                template.name,
                template.channel,
                template.body,
                json.dumps(template.required_vars),
                template.description,
                template.created_at.isoformat(),
                template.updated_at.isoformat(),
            )
        )
        conn.commit()
    return template


def get_template(template_id: str) -> Optional[NotificationTemplate]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM notification_templates WHERE template_id = ?',
            (template_id,)
        ).fetchone()
    if not row:
        return None
    return _row_to_template(row)


def list_templates() -> List[NotificationTemplate]:
    with get_connection() as conn:
        rows = conn.execute(
            'SELECT * FROM notification_templates ORDER BY updated_at DESC'
        ).fetchall()
    return [_row_to_template(row) for row in rows]


def delete_template(template_id: str) -> None:
    with get_connection() as conn:
        conn.execute('DELETE FROM notification_templates WHERE template_id = ?', (template_id,))
        conn.commit()


def save_task(task: NotificationTask) -> NotificationTask:
    task.updated_at = datetime.utcnow()
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO notification_tasks (
                task_id, template_id, channel, status, audience_json,
                variables_json, send_at, sent_at, attempts, last_error,
                rendered_body, idempotency_key, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
                status=excluded.status,
                audience_json=excluded.audience_json,
                variables_json=excluded.variables_json,
                send_at=excluded.send_at,
                sent_at=excluded.sent_at,
                attempts=excluded.attempts,
                last_error=excluded.last_error,
                rendered_body=excluded.rendered_body,
                idempotency_key=excluded.idempotency_key,
                updated_at=excluded.updated_at
            ''',
            (
                task.task_id,
                task.template_id,
                task.channel,
                task.status,
                json.dumps(task.audience),
                json.dumps(task.variables),
                _datetime_or_none(task.send_at),
                _datetime_or_none(task.sent_at),
                task.attempts,
                task.last_error,
                task.rendered_body,
                task.idempotency_key,
                task.created_at.isoformat(),
                task.updated_at.isoformat(),
            )
        )
        conn.commit()
    return task


def get_task(task_id: str) -> Optional[NotificationTask]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM notification_tasks WHERE task_id = ?',
            (task_id,)
        ).fetchone()
    if not row:
        return None
    return _row_to_task(row)


def get_task_by_idempotency(key: str) -> Optional[NotificationTask]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM notification_tasks WHERE idempotency_key = ?',
            (key,)
        ).fetchone()
    if not row:
        return None
    return _row_to_task(row)


def get_task_by_idempotency_key(key: str) -> Optional[NotificationTask]:
    return get_task_by_idempotency(key)


def get_task_by_idempotency_key(key: str) -> Optional[NotificationTask]:
    return get_task_by_idempotency(key)


def list_tasks(limit: int = 50) -> List[NotificationTask]:
    with get_connection() as conn:
        rows = conn.execute(
            'SELECT * FROM notification_tasks ORDER BY created_at DESC LIMIT ?',
            (limit,)
        ).fetchall()
    return [_row_to_task(row) for row in rows]


def _row_to_template(row) -> NotificationTemplate:
    return NotificationTemplate(
        template_id=row['template_id'],
        name=row['name'],
        channel=row['channel'],
        body=row['body'],
        required_vars=json.loads(row['required_vars']),
        description=row['description'],
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at']),
    )


def _row_to_task(row) -> NotificationTask:
    return NotificationTask(
        task_id=row['task_id'],
        template_id=row['template_id'],
        channel=row['channel'],
        status=row['status'],
        audience=json.loads(row['audience_json']),
        variables=json.loads(row['variables_json']),
        send_at=_parse_datetime(row['send_at']),
        sent_at=_parse_datetime(row['sent_at']),
        attempts=row['attempts'],
        last_error=row['last_error'],
        rendered_body=row['rendered_body'],
        idempotency_key=row['idempotency_key'],
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at']),
    )


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    return datetime.fromisoformat(value)


def _datetime_or_none(value: Optional[datetime]) -> Optional[str]:
    return value.isoformat() if value else None
