from uuid import uuid4
from decimal import Decimal
from fastapi import HTTPException, status

from .models import LedgerEntry
from .repository import save_entry
from .schemas import LedgerEntryRequest, LedgerEntryResponse


class LedgerService:
    def post_entry(self, payload: LedgerEntryRequest) -> LedgerEntryResponse:
        if not payload.lines:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='lines cannot be empty')

        total_debit = sum(Decimal(line.debit) for line in payload.lines)
        total_credit = sum(Decimal(line.credit) for line in payload.lines)
        if total_debit != total_credit:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='debit and credit must balance')

        entry_id = f"EN_{uuid4().hex}"
        entry = LedgerEntry(entry_id=entry_id, ref_type=payload.refType, ref_id=payload.refId, lines=payload.lines)
        save_entry(entry)
        return LedgerEntryResponse(entryId=entry.entry_id, refType=entry.ref_type, refId=entry.ref_id, status=entry.status)
