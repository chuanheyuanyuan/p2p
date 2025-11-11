from dataclasses import dataclass, field
from datetime import datetime
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
