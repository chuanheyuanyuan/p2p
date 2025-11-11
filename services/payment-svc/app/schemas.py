from typing import Optional
from pydantic import BaseModel, Field


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
