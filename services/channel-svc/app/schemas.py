from datetime import date, datetime
from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

EventType = Literal['install', 'register', 'apply', 'disburse']


class AttributionIn(BaseModel):
    installId: str = Field(..., min_length=3)
    channel: str = Field(..., min_length=2)
    event: EventType
    campaign: Optional[str] = None
    cost: Decimal = Field(default=Decimal('0'))
    occurredAt: datetime

    class Config:
        json_schema_extra = {
            'example': {
                'installId': 'install-001',
                'channel': 'facebook',
                'campaign': 'FB-Q4',
                'event': 'install',
                'cost': '1.2',
                'occurredAt': '2025-11-12T09:00:00Z'
            }
        }


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
