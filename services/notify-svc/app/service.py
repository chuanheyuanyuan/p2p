from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from .channel import ChannelDispatcher, ChannelDispatchError
from .config import Settings
from .models import NotificationTask, NotificationTemplate
from .repository import (
    delete_template,
    get_task,
    get_task_by_idempotency,
    get_template as repo_get_template,
    list_templates as repo_list_templates,
    save_task,
    save_template,
)
from .template_renderer import render_template


class TemplateAlreadyExistsError(Exception):
    pass


class TemplateNotFoundError(Exception):
    pass


class NotificationService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.dispatcher = ChannelDispatcher()

    def create_template(
        self,
        template_id: str,
        name: str,
        channel: str,
        body: str,
        required_vars: List[str],
        description: Optional[str],
    ) -> NotificationTemplate:
        if repo_get_template(template_id):
            raise TemplateAlreadyExistsError(f'template {template_id} already exists')
        template = NotificationTemplate(
            template_id=template_id,
            name=name,
            channel=channel,
            body=body,
            required_vars=required_vars,
            description=description,
        )
        return save_template(template)

    def update_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        channel: Optional[str] = None,
        body: Optional[str] = None,
        required_vars: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> NotificationTemplate:
        template = repo_get_template(template_id)
        if not template:
            raise TemplateNotFoundError(template_id)
        if name:
            template.name = name
        if channel:
            template.channel = channel
        if body:
            template.body = body
        if required_vars is not None:
            template.required_vars = required_vars
        if description is not None:
            template.description = description
        return save_template(template)

    def remove_template(self, template_id: str) -> None:
        if not repo_get_template(template_id):
            raise TemplateNotFoundError(template_id)
        delete_template(template_id)

    def list_templates(self) -> List[NotificationTemplate]:
        return repo_list_templates()

    def get_template(self, template_id: str) -> NotificationTemplate:
        template = repo_get_template(template_id)
        if not template:
            raise TemplateNotFoundError(template_id)
        return template

    def send_notification(
        self,
        *,
        channel: str,
        template_id: str,
        audience: Dict[str, str],
        variables: Dict[str, object],
        send_at: Optional[datetime],
        idempotency_key: Optional[str],
        locale: Optional[str],
        currency: Optional[str],
    ) -> NotificationTask:
        if idempotency_key:
            task = get_task_by_idempotency(idempotency_key)
            if task:
                return task

        template = repo_get_template(template_id)
        if not template:
            raise TemplateNotFoundError(template_id)
        if template.channel != channel:
            raise ValueError('channel mismatch with template')

        missing = [name for name in template.required_vars if name not in variables]
        if missing:
            raise ValueError(f'missing variables: {", ".join(missing)}')

        locale_to_use = locale or self.settings.default_locale
        currency_to_use = currency or self.settings.default_currency
        rendered_body = render_template(template.body, variables, locale_to_use, currency_to_use)

        task = NotificationTask(
            task_id=uuid4().hex,
            template_id=template.template_id,
            channel=channel,
            status='ENQUEUED',
            audience=audience,
            variables=variables,
            send_at=send_at,
            rendered_body=rendered_body,
            idempotency_key=idempotency_key,
        )
        save_task(task)
        print('event=NOTIFY_ENQUEUED', f'taskId={task.task_id}', f'template={task.template_id}', f'status={task.status}')

        if send_at and send_at > datetime.utcnow():
            task.status = 'SCHEDULED'
            save_task(task)
            return task

        self._dispatch(task)
        return task

    def get_task(self, task_id: str) -> Optional[NotificationTask]:
        return get_task(task_id)

    def _dispatch(self, task: NotificationTask) -> None:
        try:
            self.dispatcher.send(task, task.rendered_body or '')
            task.status = 'SENT'
            task.sent_at = datetime.utcnow()
            task.attempts += 1
            save_task(task)
            print('event=NOTIFY_SENT', f'taskId={task.task_id}', f'channel={task.channel}')
        except ChannelDispatchError as exc:
            task.status = 'FAILED'
            task.last_error = str(exc)
            task.attempts += 1
            save_task(task)
            print('event=NOTIFY_FAILED', f'taskId={task.task_id}', f'error="{task.last_error}"')
            raise
