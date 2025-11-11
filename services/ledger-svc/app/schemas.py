from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, condecimal


class LedgerLine(BaseModel):
    account: str = Field(..., min_length=2)
    debit: condecimal(max_digits=18, decimal_places=4)
    credit: condecimal(max_digits=18, decimal_places=4)
    currency: str = Field(..., min_length=3, max_length=3)
    memo: Optional[str] = None


class LedgerEntryRequest(BaseModel):
    refType: str
    refId: str
    lines: List[LedgerLine]


class LedgerEntryResponse(BaseModel):
    entryId: str
    refType: str
    refId: str
    status: str
