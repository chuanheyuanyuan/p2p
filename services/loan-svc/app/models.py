from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

LoanStatus = Literal[
    'DRAFT',
    'SUBMITTED',
    'AUTO_CHECKING',
    'AUTO_APPROVED',
    'AUTO_REJECTED'
]


@dataclass
class LoanApplication:
    loan_id: str
    user_id: str
    product_id: str
    requested_amount: float
    term_days: int
    status: LoanStatus = 'DRAFT'
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    decision_reason: Optional[str] = None
    score: Optional[int] = None


ScheduleStatus = Literal['ACTIVE', 'REPAID']


@dataclass
class RepaymentSchedule:
    loan_id: str
    currency: str
    original_amount: Decimal
    outstanding_amount: Decimal
    paid_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    status: ScheduleStatus = 'ACTIVE'
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_paid_at: Optional[datetime] = None
