from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from uuid import uuid4

from .models import NotificationTask

CHANNEL_REQUIREMENTS: Dict[str, list[str]] = {
    'sms': ['phone'],
    'whatsapp': ['phone'],
    'email': ['email'],
    'push': ['deviceToken'],
}


class ChannelDispatchError(Exception):
    pass


@dataclass
class ChannelDeliveryResult:
    provider: str
    provider_message_id: str
    delivered_at: datetime


def dispatch(task: NotificationTask) -> ChannelDeliveryResult:
    required_fields = CHANNEL_REQUIREMENTS.get(task.channel, [])
    for field in required_fields:
        if not task.audience.get(field):
            raise ChannelDispatchError(f'Field "{field}" is required for channel {task.channel}')

    delivered_at = datetime.utcnow()
    message_id = uuid4().hex
    print(
        'event=CHANNEL_DISPATCHED',
        f'channel={task.channel}',
        f'taskId={task.task_id}',
        f'messageId={message_id}',
    )
    return ChannelDeliveryResult(
        provider=f'mock-{task.channel}',
        provider_message_id=message_id,
        delivered_at=delivered_at,
    )
