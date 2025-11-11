from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, condecimal

class TermOption(BaseModel):
    termDays: int
    feeRate: float = Field(..., description='percentage, e.g. 0.15 for 15%')

class Product(BaseModel):
    productId: str
    name: str
    currency: str = 'GHS'
    amountMin: float
    amountMax: float
    defaultTerm: int
    termOptions: List[TermOption]
    enabled: bool = True

class ProductListResponse(BaseModel):
    items: List[Product]

class LoanDraftRequest(BaseModel):
    userId: str
    productId: str
    amount: float
    termDays: int

class LoanSubmitResponse(BaseModel):
    loanId: str
    status: str
    decision: Optional[str]
    score: Optional[int]


class ContractResponse(BaseModel):
    loanId: str
    contractUrl: str
    expiresAt: str


MoneyAmount = condecimal(max_digits=18, decimal_places=4)


class RepaymentApplyRequest(BaseModel):
    amount: MoneyAmount = Field(..., description='Decimal amount with 4 fraction digits')
    currency: str = Field(default='GHS', description='ISO currency code')
    paidAt: Optional[datetime] = Field(default=None, description='Timestamp of the repayment')


class RepaymentApplyResponse(BaseModel):
    loanId: str
    appliedAmount: Decimal
    remainingDue: Decimal
    currency: str
    status: str
    lastPaidAt: Optional[datetime]
