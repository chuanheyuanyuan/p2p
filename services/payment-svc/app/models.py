from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional

DisbursementStatus = Literal['PENDING', 'SUCCESS', 'FAILED']


@dataclass
class Disbursement:
    req_no: str
    loan_id: str
    amount: float
    account: dict
    channel: str
    status: DisbursementStatus = 'PENDING'
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    failure_reason: Optional[str] = None
