from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, condecimal

Money = condecimal(max_digits=18, decimal_places=4)


class CaseCreateRequest(BaseModel):
    loanId: str
    userId: str
    bucket: str
    principalDue: Money
    currency: str = 'GHS'
    assignedTo: Optional[str] = None
    notes: Optional[str] = None


class CaseActionRequest(BaseModel):
    actionType: str
    actor: str
    note: Optional[str] = None
    result: Optional[str] = None
    status: Optional[str] = Field(default=None, description='Next status for the case')
    ptpAmount: Optional[Money] = None
    ptpDueAt: Optional[datetime] = None


class ActionResponse(BaseModel):
    actionId: str
    actionType: str
    actor: str
    note: Optional[str]
    result: Optional[str]
    ptpAmount: Optional[Decimal]
    ptpDueAt: Optional[datetime]
    createdAt: datetime


class CaseResponse(BaseModel):
    caseId: str
    loanId: str
    userId: str
    bucket: str
    principalDue: Decimal
    currency: str
    status: str
    assignedTo: Optional[str]
    createdAt: datetime
    updatedAt: datetime
    ptpAmount: Optional[Decimal]
    ptpDueAt: Optional[datetime]
    lastAction: Optional[str]
    notes: Optional[str]
    actions: List[ActionResponse] = Field(default_factory=list)


class CaseListResponse(BaseModel):
    items: List[CaseResponse]


class LoanEventRequest(BaseModel):
    eventType: str = Field(description='LOAN_DUE, OVERDUE_BUCKET_CHANGED, etc.')
    loanId: str
    userId: str
    bucket: str
    principalDue: Money
    currency: str = 'GHS'
    assignedTo: Optional[str] = None
    notes: Optional[str] = None


class PaymentEventRequest(BaseModel):
    eventType: str = Field(description='REPAYMENT_POSTED')
    loanId: str
    remainingDue: Money
    actor: Optional[str] = None
