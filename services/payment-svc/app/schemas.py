from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, condecimal


class AccountInfo(BaseModel):
    type: str
    number: str
    holderName: str


class DisbursementRequest(BaseModel):
    loanId: str
    amount: float
    channel: str = 'mock-channel'
    account: AccountInfo


class DisbursementResponse(BaseModel):
    reqNo: str
    status: str


class CallbackPayload(BaseModel):
    reqNo: str
    status: str
    failureReason: Optional[str] = None


MoneyAmount = condecimal(max_digits=18, decimal_places=4)


class RepaymentRequest(BaseModel):
    loanId: str
    amount: MoneyAmount
    currency: str
    channel: str
    txnRef: str
    paidAt: Optional[datetime] = None


class RepaymentResponse(BaseModel):
    repaymentId: str
    loanId: str
    status: str
    appliedAmount: Decimal
    remainingDue: Decimal
    currency: str
    txnRef: str
    paidAt: datetime
