from datetime import datetime
from decimal import Decimal
from typing import Optional

from .database import get_connection
from .models import RepaymentSchedule


def save_schedule(schedule: RepaymentSchedule) -> RepaymentSchedule:
    schedule.updated_at = datetime.utcnow()
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO repayment_schedules (
                loan_id, currency, original_amount, outstanding_amount,
                paid_amount, status, created_at, updated_at, last_paid_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(loan_id) DO UPDATE SET
                currency=excluded.currency,
                original_amount=excluded.original_amount,
                outstanding_amount=excluded.outstanding_amount,
                paid_amount=excluded.paid_amount,
                status=excluded.status,
                updated_at=excluded.updated_at,
                last_paid_at=excluded.last_paid_at
            ''',
            (
                schedule.loan_id,
                schedule.currency,
                str(schedule.original_amount),
                str(schedule.outstanding_amount),
                str(schedule.paid_amount),
                schedule.status,
                schedule.created_at.isoformat(),
                schedule.updated_at.isoformat(),
                schedule.last_paid_at.isoformat() if schedule.last_paid_at else None,
            )
        )
        conn.commit()
    return schedule


def get_schedule(loan_id: str) -> Optional[RepaymentSchedule]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM repayment_schedules WHERE loan_id = ?',
            (loan_id,)
        ).fetchone()
    if not row:
        return None
    return RepaymentSchedule(
        loan_id=row['loan_id'],
        currency=row['currency'],
        original_amount=Decimal(row['original_amount']),
        outstanding_amount=Decimal(row['outstanding_amount']),
        paid_amount=Decimal(row['paid_amount']),
        status=row['status'],
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at']),
        last_paid_at=datetime.fromisoformat(row['last_paid_at']) if row['last_paid_at'] else None,
    )
