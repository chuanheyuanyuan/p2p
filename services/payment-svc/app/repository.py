from datetime import datetime
from typing import Dict, Optional

from .models import Disbursement, Repayment

_disbursement_store: Dict[str, Disbursement] = {}
_repayment_store: Dict[str, Repayment] = {}
_repayment_index: Dict[str, str] = {}


def save_disbursement(disb: Disbursement) -> Disbursement:
    disb.updated_at = datetime.utcnow()
    _disbursement_store[disb.req_no] = disb
    return disb


def get_disbursement(req_no: str) -> Optional[Disbursement]:
    return _disbursement_store.get(req_no)


def list_disbursements() -> list[Disbursement]:
    return list(_disbursement_store.values())


def save_repayment(rep: Repayment) -> Repayment:
    rep.updated_at = datetime.utcnow()
    _repayment_store[rep.repayment_id] = rep
    _repayment_index[rep.txn_ref] = rep.repayment_id
    return rep


def get_repayment_by_txn(txn_ref: str) -> Optional[Repayment]:
    rep_id = _repayment_index.get(txn_ref)
    if not rep_id:
        return None
    return _repayment_store.get(rep_id)


def list_repayments() -> list[Repayment]:
    return list(_repayment_store.values())
