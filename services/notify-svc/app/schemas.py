from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

from .models import NotificationTask


class Audience(BaseModel):
    userId: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    deviceToken: Optional[str] = None


class NotificationRequest(BaseModel):
    channel: Literal['sms', 'email', 'push', 'whatsapp']
    template: str
    audience: Audience
    variables: Dict[str, Any] = Field(default_factory=dict)
    sendAt: Optional[datetime] = None


class NotificationTaskResponse(BaseModel):
    taskId: str
    status: str
    channel: str
    template: str
    sendAt: Optional[datetime]
    deliveredAt: Optional[datetime]
    createdAt: datetime
    updatedAt: datetime
    lastError: Optional[str]
    audience: Audience
    variables: Dict[str, Any]
    body: str

    @classmethod
    def from_model(cls, task: NotificationTask) -> 'NotificationTaskResponse':
        return cls(
            taskId=task.task_id,
            status=task.status,
            channel=task.channel,
            template=task.template_id,
            sendAt=task.send_at,
            deliveredAt=task.sent_at,
            createdAt=task.created_at,
            updatedAt=task.updated_at,
            lastError=task.last_error,
            audience=Audience.model_validate(task.audience),
            variables=task.variables,
            body=task.rendered_body or '',
        )
