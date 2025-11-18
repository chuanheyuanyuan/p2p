from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class LoanSummary(BaseModel):
    loanId: str
    productId: str
    amount: Decimal
    termDays: int
    status: str
    outstandingAmount: Decimal = Field(default=Decimal('0'))
    originalAmount: Decimal = Field(default=Decimal('0'))
    lastPaidAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime


class LoanListResponse(BaseModel):
    items: List[LoanSummary]
    total: int


class LoanCreateRequest(BaseModel):
    productId: str
    amount: float
    termDays: int


class LoanCreateResponse(BaseModel):
    loanId: str
    status: str
    decision: Optional[str] = None
    score: Optional[int] = None


class DashboardMetrics(BaseModel):
    totalOutstanding: Decimal = Field(default=Decimal('0'))
    activeLoans: int = 0
    lastActivityAt: Optional[datetime] = None


class ProductTermOption(BaseModel):
    termDays: int
    feeRate: float


class ProductSummary(BaseModel):
    productId: str
    name: str
    currency: str
    amountMin: float
    amountMax: float
    defaultTerm: int
    termOptions: List[ProductTermOption]


class DashboardResponse(BaseModel):
    userId: str
    metrics: DashboardMetrics
    loans: List[LoanSummary]
    recommendations: List[ProductSummary]
