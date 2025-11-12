from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Literal, Optional

NotificationStatus = Literal['ENQUEUED', 'SCHEDULED', 'SENT', 'FAILED']


@dataclass
class NotificationTemplate:
    template_id: str
    name: str
    channel: str
    body: str
    required_vars: List[str] = field(default_factory=list)
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NotificationTask:
    task_id: str
    template_id: str
    channel: str
    status: NotificationStatus
    audience: Dict[str, str]
    variables: Dict[str, object]
    send_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    attempts: int = 0
    last_error: Optional[str] = None
    rendered_body: Optional[str] = None
    idempotency_key: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
