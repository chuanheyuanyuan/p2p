import json
from datetime import datetime
from typing import Optional

from fastapi.encoders import jsonable_encoder

from .database import get_connection
from .models import LedgerEntry
from .schemas import LedgerLine


def save_entry(entry: LedgerEntry) -> LedgerEntry:
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO ledger_entries (entry_id, ref_type, ref_id, status, lines_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(entry_id) DO UPDATE SET
                status=excluded.status,
                lines_json=excluded.lines_json
            ''',
            (
                entry.entry_id,
                entry.ref_type,
                entry.ref_id,
                entry.status,
                json.dumps(jsonable_encoder(entry.lines)),
                entry.created_at.isoformat(),
            )
        )
        conn.commit()
    return entry


def get_by_ref(ref_id: str) -> Optional[LedgerEntry]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM ledger_entries WHERE ref_id = ? ORDER BY created_at DESC LIMIT 1',
            (ref_id,)
        ).fetchone()
    if not row:
        return None
    lines_payload = json.loads(row['lines_json'])
    lines = [LedgerLine(**payload) for payload in lines_payload]
    return LedgerEntry(
        entry_id=row['entry_id'],
        ref_type=row['ref_type'],
        ref_id=row['ref_id'],
        lines=lines,
        status=row['status'],
        created_at=datetime.fromisoformat(row['created_at']),
    )
