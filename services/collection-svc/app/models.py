from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Literal, Optional

Bucket = Literal['D0', 'D1', 'D2', 'D3', 'D7', 'D15', 'D30', 'D60', 'WRITE_OFF']
CaseStatus = Literal['OPEN', 'IN_PROGRESS', 'PTP', 'BROKEN_PTP', 'PAID', 'TRANSFER', 'WRITE_OFF']
ActionType = Literal['CALL', 'SMS', 'WHATSAPP', 'EMAIL', 'NOTE', 'VISIT']


@dataclass
class CollectionAction:
    action_id: str
    case_id: str
    action_type: ActionType
    actor: str
    note: Optional[str] = None
    result: Optional[str] = None
    ptp_amount: Optional[Decimal] = None
    ptp_due_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CollectionCase:
    case_id: str
    loan_id: str
    user_id: str
    bucket: Bucket
    principal_due: Decimal
    currency: str
    status: CaseStatus = 'OPEN'
    assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_action: Optional[str] = None
    ptp_amount: Optional[Decimal] = None
    ptp_due_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    notes: Optional[str] = None
    actions: List[CollectionAction] = field(default_factory=list)
