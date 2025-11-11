from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .schemas import LedgerLine


@dataclass
class LedgerEntry:
    entry_id: str
    ref_type: str
    ref_id: str
    lines: List[LedgerLine]
    status: str = 'POSTED'
    created_at: datetime = field(default_factory=datetime.utcnow)
