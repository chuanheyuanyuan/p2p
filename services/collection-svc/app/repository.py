from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from .database import get_connection
from .models import CollectionAction, CollectionCase


def save_case(case: CollectionCase) -> CollectionCase:
    case.updated_at = datetime.utcnow()
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO collection_cases (
                case_id, loan_id, user_id, bucket, principal_due, currency,
                status, assigned_to, created_at, updated_at, last_action,
                ptp_amount, ptp_due_at, resolved_at, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(case_id) DO UPDATE SET
                bucket=excluded.bucket,
                principal_due=excluded.principal_due,
                currency=excluded.currency,
                status=excluded.status,
                assigned_to=excluded.assigned_to,
                updated_at=excluded.updated_at,
                last_action=excluded.last_action,
                ptp_amount=excluded.ptp_amount,
                ptp_due_at=excluded.ptp_due_at,
                resolved_at=excluded.resolved_at,
                notes=excluded.notes
            ''',
            (
                case.case_id,
                case.loan_id,
                case.user_id,
                case.bucket,
                str(case.principal_due),
                case.currency,
                case.status,
                case.assigned_to,
                case.created_at.isoformat(),
                case.updated_at.isoformat(),
                case.last_action,
                str(case.ptp_amount) if case.ptp_amount is not None else None,
                case.ptp_due_at.isoformat() if case.ptp_due_at else None,
                case.resolved_at.isoformat() if case.resolved_at else None,
                case.notes,
            )
        )
        conn.commit()
    return case


def _row_to_case(row) -> CollectionCase:
    case = CollectionCase(
        case_id=row['case_id'],
        loan_id=row['loan_id'],
        user_id=row['user_id'],
        bucket=row['bucket'],
        principal_due=Decimal(row['principal_due']),
        currency=row['currency'],
        status=row['status'],
        assigned_to=row['assigned_to'],
        created_at=datetime.fromisoformat(row['created_at']),
        updated_at=datetime.fromisoformat(row['updated_at']),
        last_action=row['last_action'],
        ptp_amount=Decimal(row['ptp_amount']) if row['ptp_amount'] else None,
        ptp_due_at=datetime.fromisoformat(row['ptp_due_at']) if row['ptp_due_at'] else None,
        resolved_at=datetime.fromisoformat(row['resolved_at']) if row['resolved_at'] else None,
        notes=row['notes'],
    )
    case.actions = list_actions_by_case(case.case_id)
    return case


def get_case(case_id: str) -> Optional[CollectionCase]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM collection_cases WHERE case_id = ?',
            (case_id,)
        ).fetchone()
    if not row:
        return None
    return _row_to_case(row)


def find_active_case_by_loan(loan_id: str) -> Optional[CollectionCase]:
    with get_connection() as conn:
        row = conn.execute(
            '''
            SELECT * FROM collection_cases
            WHERE loan_id = ? AND status NOT IN ('PAID','TRANSFER','WRITE_OFF')
            ''',
            (loan_id,)
        ).fetchone()
    if not row:
        return None
    return _row_to_case(row)


def get_case_by_loan(loan_id: str) -> Optional[CollectionCase]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM collection_cases WHERE loan_id = ?',
            (loan_id,)
        ).fetchone()
    if not row:
        return None
    return _row_to_case(row)


def list_cases(
    bucket: Optional[str] = None,
    status: Optional[str] = None,
    assignee: Optional[str] = None
) -> List[CollectionCase]:
    query = 'SELECT * FROM collection_cases WHERE 1=1'
    params: list = []
    if bucket:
        query += ' AND bucket = ?'
        params.append(bucket)
    if status:
        query += ' AND status = ?'
        params.append(status)
    if assignee:
        query += ' AND assigned_to = ?'
        params.append(assignee)
    query += ' ORDER BY created_at'
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_case(row) for row in rows]


def add_action(case: CollectionCase, action: CollectionAction) -> CollectionAction:
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO collection_actions (
                action_id, case_id, action_type, actor, note, result,
                ptp_amount, ptp_due_at, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                action.action_id,
                action.case_id,
                action.action_type,
                action.actor,
                action.note,
                action.result,
                str(action.ptp_amount) if action.ptp_amount is not None else None,
                action.ptp_due_at.isoformat() if action.ptp_due_at else None,
                action.created_at.isoformat(),
            )
        )
        conn.commit()
    case.actions.append(action)
    case.last_action = action.action_type
    case.updated_at = datetime.utcnow()
    save_case(case)
    return action


def list_actions_by_case(case_id: str) -> List[CollectionAction]:
    with get_connection() as conn:
        rows = conn.execute(
            'SELECT * FROM collection_actions WHERE case_id = ? ORDER BY created_at',
            (case_id,)
        ).fetchall()
    actions: List[CollectionAction] = []
    for row in rows:
        actions.append(
            CollectionAction(
                action_id=row['action_id'],
                case_id=row['case_id'],
                action_type=row['action_type'],
                actor=row['actor'],
                note=row['note'],
                result=row['result'],
                ptp_amount=Decimal(row['ptp_amount']) if row['ptp_amount'] else None,
                ptp_due_at=datetime.fromisoformat(row['ptp_due_at']) if row['ptp_due_at'] else None,
                created_at=datetime.fromisoformat(row['created_at']),
            )
        )
    return actions
