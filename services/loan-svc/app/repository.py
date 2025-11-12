from datetime import datetime
from typing import Optional

from .database import get_connection
from .models import LoanApplication


def save_application(app: LoanApplication) -> LoanApplication:
    now = datetime.utcnow()
    app.updated_at = now
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO loan_applications (
                loan_id, user_id, product_id, requested_amount, term_days,
                status, created_at, updated_at, decision_reason, score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(loan_id) DO UPDATE SET
                user_id=excluded.user_id,
                product_id=excluded.product_id,
                requested_amount=excluded.requested_amount,
                term_days=excluded.term_days,
                status=excluded.status,
                updated_at=excluded.updated_at,
                decision_reason=excluded.decision_reason,
                score=excluded.score
            ''',
            (
                app.loan_id,
                app.user_id,
                app.product_id,
                app.requested_amount,
                app.term_days,
                app.status,
                app.created_at.isoformat(),
                app.updated_at.isoformat(),
                app.decision_reason,
                app.score,
            )
        )
        conn.commit()
    return app


def get_application(loan_id: str) -> Optional[LoanApplication]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM loan_applications WHERE loan_id = ?',
            (loan_id,)
        ).fetchone()
    if not row:
        return None
    return LoanApplication(
        loan_id=row['loan_id'],
        user_id=row['user_id'],
        product_id=row['product_id'],
        requested_amount=row['requested_amount'],
        term_days=row['term_days'],
        status=row['status'],
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at']),
        decision_reason=row['decision_reason'],
        score=row['score'],
    )
