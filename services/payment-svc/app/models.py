from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
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


RepaymentStatus = Literal['POSTED', 'FAILED']


@dataclass
class Repayment:
    repayment_id: str
    loan_id: str
    amount: Decimal
    currency: str
    channel: str
    txn_ref: str
    status: RepaymentStatus = 'POSTED'
    applied_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    remaining_due: Decimal = field(default_factory=lambda: Decimal('0'))
    paid_at: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
