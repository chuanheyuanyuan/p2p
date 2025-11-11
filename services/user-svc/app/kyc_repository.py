import json
from datetime import datetime
from typing import Optional

from .database import get_conn

KYC_PENDING = 'PENDING'
KYC_REVIEWING = 'REVIEWING'
KYC_APPROVED = 'APPROVED'
KYC_REJECTED = 'REJECTED'


def upsert_kyc(
    user_id: str,
    *,
    status: str,
    doc_type: Optional[str],
    doc_number: Optional[str],
    selfie_url: Optional[str],
    doc_front_url: Optional[str],
    doc_back_url: Optional[str],
    meta: dict,
    reviewer: Optional[str] = None,
    reviewed_at: Optional[datetime] = None
) -> dict:
    meta_json = json.dumps(meta, ensure_ascii=False)
    reviewed_at_iso = reviewed_at.isoformat() if reviewed_at else None
    sql = (
        "INSERT INTO user_kyc (user_id, kyc_status, doc_type, doc_number, selfie_url, doc_front_url, doc_back_url, meta_json, reviewer, reviewed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(user_id) DO UPDATE SET "
        "kyc_status=excluded.kyc_status, doc_type=excluded.doc_type, doc_number=excluded.doc_number, "
        "selfie_url=excluded.selfie_url, doc_front_url=excluded.doc_front_url, doc_back_url=excluded.doc_back_url, "
        "meta_json=excluded.meta_json, reviewer=excluded.reviewer, reviewed_at=excluded.reviewed_at, updated_at=datetime('now')"
    )
    with get_conn() as conn:
        conn.execute(
            sql,
            (user_id, status, doc_type, doc_number, selfie_url, doc_front_url, doc_back_url, meta_json, reviewer, reviewed_at_iso)
        )
        row = conn.execute(
            "SELECT user_id, kyc_status, doc_type, doc_number, selfie_url, doc_front_url, doc_back_url, meta_json, reviewer, reviewed_at, updated_at FROM user_kyc WHERE user_id=?",
            (user_id,)
        ).fetchone()
        return dict(row)
