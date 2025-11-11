from typing import List, Optional
from pydantic import BaseModel, Field, conlist


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
