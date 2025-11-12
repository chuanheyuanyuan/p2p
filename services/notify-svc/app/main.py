from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .channel_client import ChannelDispatchError, dispatch
from .config import get_settings
from .models import NotificationTask
from .repository import get_task, get_task_by_idempotency_key, save_task
from .schemas import NotificationRequest, NotificationTaskResponse
from .template_engine import (
    ChannelNotSupportedError,
    MissingTemplateVariableError,
    TemplateNotFoundError,
    TemplateStore,
)

settings = get_settings()
template_store = TemplateStore(settings.templates_path)

app = FastAPI(title=settings.app_name, version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/healthz')
def healthz() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.post('/notifications/send', response_model=NotificationTaskResponse, status_code=202)
def send_notification(
    payload: NotificationRequest,
    idempotency_key: Optional[str] = Header(default=None, alias='X-Idempotency-Key'),
) -> NotificationTaskResponse:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail='X-Idempotency-Key header is required')

    existing = get_task_by_idempotency_key(idempotency_key)
    if existing:
        return NotificationTaskResponse.from_model(existing)

    try:
        rendered_body = template_store.render(payload.template, payload.channel, payload.variables)
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChannelNotSupportedError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except MissingTemplateVariableError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    send_at = _normalize_datetime(payload.sendAt)
    should_schedule = send_at is not None and send_at > datetime.utcnow()
    task = NotificationTask(
        task_id=uuid4().hex,
        channel=payload.channel,
        template_id=payload.template,
        audience=payload.audience.model_dump(exclude_none=True),
        variables=payload.variables,
        rendered_body=rendered_body,
        status='SCHEDULED' if should_schedule else 'ENQUEUED',
        send_at=send_at,
        idempotency_key=idempotency_key,
    )
    save_task(task)
    _emit_event('NOTIFY_ENQUEUED', task, extra={'scheduled': should_schedule})

    if not should_schedule:
        _deliver_task(task)

    return NotificationTaskResponse.from_model(task)


@app.get('/notifications/tasks/{task_id}', response_model=NotificationTaskResponse)
def get_notification_task(task_id: str) -> NotificationTaskResponse:
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    return NotificationTaskResponse.from_model(task)


def _deliver_task(task: NotificationTask) -> None:
    try:
        result = dispatch(task)
    except ChannelDispatchError as exc:
        task.status = 'FAILED'
        task.last_error = str(exc)
        task.attempts += 1
        save_task(task)
        _emit_event('NOTIFY_FAILED', task, extra={'error': str(exc)})
        return

    task.status = 'SENT'
    task.sent_at = result.delivered_at
    task.last_error = None
    task.attempts += 1
    save_task(task)
    _emit_event('NOTIFY_SENT', task, extra={'messageId': result.provider_message_id})


def _emit_event(event: str, task: NotificationTask, extra: Optional[dict] = None) -> None:
    parts = [
        f'event={event}',
        f'taskId={task.task_id}',
        f'template={task.template_id}',
        f'channel={task.channel}',
        f'status={task.status}',
    ]
    if extra:
        for key, value in extra.items():
            parts.append(f'{key}={value}')
    print(' '.join(parts))


def _normalize_datetime(value: Optional[datetime]) -> Optional[datetime]:
    if not value:
        return None
    if value.tzinfo:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value
