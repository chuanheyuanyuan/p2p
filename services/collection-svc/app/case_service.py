from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
from uuid import uuid4

from fastapi import HTTPException, status

from .assignment import AssignmentService
from .models import CollectionAction, CollectionCase
from .repository import (
    add_action,
    find_active_case_by_loan,
    get_case,
    list_cases as repo_list_cases,
    save_case,
)

MONEY_QUANT = Decimal('0.0001')
RESOLVED_STATUSES = {'PAID', 'TRANSFER', 'WRITE_OFF'}
SUPPORTED_BUCKETS = {'D0', 'D1', 'D2', 'D3', 'D7', 'D15', 'D30', 'D60', 'WRITE_OFF'}
ALLOWED_ACTIONS = {'CALL', 'SMS', 'WHATSAPP', 'EMAIL', 'NOTE', 'VISIT'}
ALLOWED_TRANSITIONS = {
    'OPEN': {'IN_PROGRESS', 'PTP', 'TRANSFER', 'WRITE_OFF'},
    'IN_PROGRESS': {'PTP', 'BROKEN_PTP', 'PAID', 'TRANSFER', 'WRITE_OFF'},
    'PTP': {'PAID', 'BROKEN_PTP', 'TRANSFER', 'WRITE_OFF'},
    'BROKEN_PTP': {'IN_PROGRESS', 'TRANSFER', 'WRITE_OFF'},
    'PAID': set(),
    'TRANSFER': set(),
    'WRITE_OFF': set(),
}
VALID_STATUSES = set(ALLOWED_TRANSITIONS.keys())


def normalize_amount(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


class CaseService:
    def __init__(self, assignment: AssignmentService) -> None:
        self.assignment = assignment

    def _ensure_case(self, case_id: str) -> CollectionCase:
        case = get_case(case_id)
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='case not found')
        return case

    def create_case(
        self,
        loan_id: str,
        user_id: str,
        bucket: str,
        principal_due: Decimal,
        currency: str,
        assigned_to: Optional[str],
        notes: Optional[str]
    ) -> CollectionCase:
        existing = find_active_case_by_loan(loan_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='active case already exists for loan')
        bucket_code = bucket.upper()
        if bucket_code not in SUPPORTED_BUCKETS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid bucket')
        normalized_amount = normalize_amount(principal_due)
        if normalized_amount <= Decimal('0'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='principalDue must be positive')
        assigned = self.assignment.pick(assigned_to)
        case = CollectionCase(
            case_id=uuid4().hex,
            loan_id=loan_id,
            user_id=user_id,
            bucket=bucket_code,
            principal_due=normalized_amount,
            currency=currency,
            assigned_to=assigned,
            notes=notes
        )
        save_case(case)
        self._emit_case_created(case)
        return case

    def list_cases(self, bucket: Optional[str], status: Optional[str], assignee: Optional[str]) -> list[CollectionCase]:
        status_filter = status.upper() if status else None
        bucket_filter = bucket.upper() if bucket else None
        return repo_list_cases(bucket=bucket_filter, status=status_filter, assignee=assignee)

    def get_case(self, case_id: str) -> CollectionCase:
        return self._ensure_case(case_id)

    def record_action(
        self,
        case_id: str,
        action_type: str,
        actor: str,
        note: Optional[str],
        result: Optional[str],
        status_after: Optional[str],
        ptp_amount: Optional[Decimal],
        ptp_due_at: Optional[datetime]
    ) -> CollectionAction:
        case = self._ensure_case(case_id)
        if case.status in RESOLVED_STATUSES:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='case already resolved')

        normalized_type = action_type.upper()
        if normalized_type not in ALLOWED_ACTIONS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid actionType')
        target_status = status_after.upper() if status_after else None

        action = CollectionAction(
            action_id=uuid4().hex,
            case_id=case.case_id,
            action_type=normalized_type,
            actor=actor,
            note=note,
            result=result,
            ptp_amount=normalize_amount(ptp_amount) if ptp_amount is not None else None,
            ptp_due_at=ptp_due_at
        )
        add_action(case, action)

        if ptp_amount is not None or ptp_due_at is not None:
            case.ptp_amount = action.ptp_amount
            case.ptp_due_at = ptp_due_at
            target_status = target_status or 'PTP'
            self._emit_ptp_set(case)

        if target_status:
            self._apply_transition(case, target_status)

        save_case(case)
        self._emit_action_logged(case, action)
        return action

    def sync_case_from_loan_event(
        self,
        loan_id: str,
        user_id: str,
        bucket: str,
        principal_due: Decimal,
        currency: str,
        assigned_to: Optional[str] = None,
        notes: Optional[str] = None
    ) -> CollectionCase:
        bucket_code = bucket.upper()
        if bucket_code not in SUPPORTED_BUCKETS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid bucket')
        normalized_amount = normalize_amount(principal_due)
        if normalized_amount <= Decimal('0'):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='principalDue must be positive')
        case = find_active_case_by_loan(loan_id)
        if case:
            case.bucket = bucket_code
            case.principal_due = normalized_amount
            case.currency = currency
            case.notes = notes or case.notes
            if assigned_to:
                case.assigned_to = assigned_to
            save_case(case)
            self._emit_case_bucket_updated(case)
            return case
        return self.create_case(
            loan_id=loan_id,
            user_id=user_id,
            bucket=bucket_code,
            principal_due=normalized_amount,
            currency=currency,
            assigned_to=assigned_to,
            notes=notes
        )

    def apply_payment_event(
        self,
        loan_id: str,
        remaining_due: Decimal,
        event_type: str,
        actor: Optional[str] = None
    ) -> Optional[CollectionCase]:
        case = find_active_case_by_loan(loan_id)
        if not case:
            return None
        normalized_remaining = normalize_amount(remaining_due)
        case.principal_due = normalized_remaining
        if normalized_remaining <= Decimal('0'):
            self._apply_transition(case, 'PAID')
        elif case.status == 'PTP':
            self._apply_transition(case, 'BROKEN_PTP')
        save_case(case)
        self._emit_payment_applied(case, event_type, actor)
        return case

    def _apply_transition(self, case: CollectionCase, next_status: str) -> None:
        if case.status == next_status:
            return
        if next_status not in VALID_STATUSES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid status')
        allowed = ALLOWED_TRANSITIONS.get(case.status, set())
        if next_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'invalid transition {case.status} -> {next_status}'
            )
        case.status = next_status
        if next_status in RESOLVED_STATUSES:
            case.resolved_at = datetime.utcnow()

    def _emit_case_created(self, case: CollectionCase) -> None:
        print(
            'event=CASE_CREATED',
            f"caseId={case.case_id}",
            f"loanId={case.loan_id}",
            f"bucket={case.bucket}",
            f"assignee={case.assigned_to}"
        )

    def _emit_action_logged(self, case: CollectionCase, action: CollectionAction) -> None:
        print(
            'event=CASE_ACTION_LOGGED',
            f"caseId={case.case_id}",
            f"actionId={action.action_id}",
            f"type={action.action_type}",
            f"actor={action.actor}",
            f"status={case.status}"
        )

    def _emit_ptp_set(self, case: CollectionCase) -> None:
        print(
            'event=PTP_PROMISE_SET',
            f"caseId={case.case_id}",
            f"ptpAmount={case.ptp_amount}",
            f"ptpDueAt={case.ptp_due_at.isoformat() if case.ptp_due_at else 'na'}"
        )

    def _emit_case_bucket_updated(self, case: CollectionCase) -> None:
        print(
            'event=CASE_BUCKET_SYNCED',
            f"caseId={case.case_id}",
            f"bucket={case.bucket}",
            f"principalDue={case.principal_due}"
        )

    def _emit_payment_applied(self, case: CollectionCase, event_type: str, actor: Optional[str]) -> None:
        print(
            'event=CASE_PAYMENT_APPLIED',
            f"caseId={case.case_id}",
            f"eventType={event_type}",
            f"principalDue={case.principal_due}",
            f"status={case.status}",
            f"actor={actor or 'system'}"
        )
