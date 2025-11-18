from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class AuditEventCreate(BaseModel):
    actorId: str = Field(..., min_length=3, max_length=64)
    actorType: str = Field(..., min_length=3, max_length=32)
    action: str = Field(..., min_length=3, max_length=64)
    resourceType: str = Field(..., min_length=3, max_length=64)
    resourceId: str = Field(..., min_length=1, max_length=64)
    severity: str = Field(default='INFO', pattern='^(INFO|WARN|ERROR)$')
    payload: Optional[Dict[str, Any]] = Field(default=None)
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None
    occurredAt: datetime = Field(default_factory=datetime.utcnow)


class AuditEvent(AuditEventCreate):
    eventId: str
    recordedAt: str
    sourceService: Optional[str] = None


class AuditEventList(BaseModel):
    items: List[AuditEvent]
    total: int
