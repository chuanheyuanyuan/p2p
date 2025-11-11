from datetime import datetime, date
from typing import Literal, Optional, List
from pydantic import BaseModel, Field

EventType = Literal['install', 'register', 'apply', 'disburse']


class AttributionIn(BaseModel):
    installId: str = Field(..., alias='installId', min_length=3)
    channel: str
    event: EventType
    campaign: Optional[str] = None
    cost: float = 0
    occurredAt: datetime

    class Config:
        populate_by_name = True


class AttributionAccepted(BaseModel):
    installId: str
    event: EventType
    acceptedAt: datetime = Field(default_factory=datetime.utcnow)


class FunnelRow(BaseModel):
    date: date
    channel: str
    installs: int = 0
    registrations: int = 0
    applications: int = 0
    disbursements: int = 0
    spend: float = 0


class FunnelResponse(BaseModel):
    items: List[FunnelRow]
    total: int
