from typing import Dict, Optional

from .models import LedgerEntry

_store: Dict[str, LedgerEntry] = {}


def save_entry(entry: LedgerEntry) -> LedgerEntry:
    _store[entry.entry_id] = entry
    return entry


def get_by_ref(ref_id: str) -> Optional[LedgerEntry]:
    return next((entry for entry in _store.values() if entry.ref_id == ref_id), None)
