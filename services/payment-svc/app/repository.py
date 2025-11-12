import json
from datetime import datetime
from decimal import Decimal
from typing import Optional

from .database import get_connection
from .models import Disbursement, Repayment


def _row_to_disbursement(row) -> Disbursement:
    return Disbursement(
        req_no=row['req_no'],
        loan_id=row['loan_id'],
        amount=float(row['amount']),
        account=json.loads(row['account_json']),
        channel=row['channel'],
        status=row['status'],
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at']),
        failure_reason=row['failure_reason'],
    )


def save_disbursement(disb: Disbursement) -> Disbursement:
    disb.updated_at = datetime.utcnow()
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO disbursements (
                req_no, loan_id, amount, account_json, channel,
                status, failure_reason, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(req_no) DO UPDATE SET
                status=excluded.status,
                failure_reason=excluded.failure_reason,
                updated_at=excluded.updated_at
            ''',
            (
                disb.req_no,
                disb.loan_id,
                str(disb.amount),
                json.dumps(disb.account),
                disb.channel,
                disb.status,
                disb.failure_reason,
                disb.created_at.isoformat(),
                disb.updated_at.isoformat(),
            )
        )
        conn.commit()
    return disb


def get_disbursement(req_no: str) -> Optional[Disbursement]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM disbursements WHERE req_no = ?',
            (req_no,)
        ).fetchone()
    if not row:
        return None
    return _row_to_disbursement(row)


def list_disbursements() -> list[Disbursement]:
    with get_connection() as conn:
        rows = conn.execute('SELECT * FROM disbursements ORDER BY created_at DESC').fetchall()
    return [_row_to_disbursement(row) for row in rows]


def _row_to_repayment(row) -> Repayment:
    return Repayment(
        repayment_id=row['repayment_id'],
        loan_id=row['loan_id'],
        amount=Decimal(row['amount']),
        currency=row['currency'],
        channel=row['channel'],
        txn_ref=row['txn_ref'],
        status=row['status'],
        applied_amount=Decimal(row['applied_amount']),
        remaining_due=Decimal(row['remaining_due']),
        paid_at=datetime.fromisoformat(row['paid_at']),
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at']),
    )


def save_repayment(rep: Repayment) -> Repayment:
    rep.updated_at = datetime.utcnow()
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO repayments (
                repayment_id, loan_id, amount, currency, channel, txn_ref,
                status, applied_amount, remaining_due, paid_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(repayment_id) DO UPDATE SET
                status=excluded.status,
                applied_amount=excluded.applied_amount,
                remaining_due=excluded.remaining_due,
                updated_at=excluded.updated_at
            ''',
            (
                rep.repayment_id,
                rep.loan_id,
                str(rep.amount),
                rep.currency,
                rep.channel,
                rep.txn_ref,
                rep.status,
                str(rep.applied_amount),
                str(rep.remaining_due),
                rep.paid_at.isoformat(),
                rep.created_at.isoformat(),
                rep.updated_at.isoformat(),
            )
        )
        conn.commit()
    return rep


def get_repayment_by_txn(txn_ref: str) -> Optional[Repayment]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM repayments WHERE txn_ref = ?',
            (txn_ref,)
        ).fetchone()
    if not row:
        return None
    return _row_to_repayment(row)


def list_repayments() -> list[Repayment]:
    with get_connection() as conn:
        rows = conn.execute('SELECT * FROM repayments ORDER BY created_at DESC').fetchall()
    return [_row_to_repayment(row) for row in rows]
