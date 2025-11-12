from typing import Any, Dict

from .models import NotificationTask


class ChannelDispatchError(Exception):
    pass


class ChannelDispatcher:
    def send(self, task: NotificationTask, body: str) -> None:
        validator = _CHANNEL_REQUIREMENTS.get(task.channel)
        if validator and not validator(task.audience):
            raise ChannelDispatchError(f'missing audience target for channel={task.channel}')
        print(
            'event=NOTIFY_DISPATCH',
            f'channel={task.channel}',
            f"to={task.audience.get('phone') or task.audience.get('email') or task.audience.get('userId')}",
            f'taskId={task.task_id}'
        )
        print('payload=', body)


def _sms_requirements(audience: Dict[str, Any]) -> bool:
    return bool(audience.get('phone'))


def _email_requirements(audience: Dict[str, Any]) -> bool:
    return bool(audience.get('email'))


def _push_requirements(audience: Dict[str, Any]) -> bool:
    return bool(audience.get('deviceToken'))


_CHANNEL_REQUIREMENTS = {
    'sms': _sms_requirements,
    'whatsapp': _sms_requirements,
    'email': _email_requirements,
    'push': _push_requirements,
}
