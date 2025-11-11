from datetime import datetime
from typing import Dict, Optional

from .models import Disbursement

_store: Dict[str, Disbursement] = {}


def save_disbursement(disb: Disbursement) -> Disbursement:
    disb.updated_at = datetime.utcnow()
    _store[disb.req_no] = disb
    return disb


def get_disbursement(req_no: str) -> Optional[Disbursement]:
    return _store.get(req_no)


def list_disbursements() -> list[Disbursement]:
    return list(_store.values())
