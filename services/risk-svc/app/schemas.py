from pydantic import BaseModel, Field
from typing import Dict, Optional


class LoanInfo(BaseModel):
    loanId: str
    amount: float
    termDays: int
    productId: str


class EvaluationSignals(BaseModel):
    device: Optional[Dict] = None
    kyc: Optional[Dict] = None
    history: Optional[Dict] = None


class EvaluationRequest(BaseModel):
    userId: str = Field(..., min_length=3)
    loan: LoanInfo
    signals: EvaluationSignals


class EvaluationResponse(BaseModel):
    decision: str
    score: int
    reasons: list[str]
