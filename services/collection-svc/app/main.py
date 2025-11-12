from typing import Optional

from fastapi import FastAPI, Path, Query
from fastapi.middleware.cors import CORSMiddleware

from .assignment import AssignmentService
from .case_service import CaseService
from .config import get_settings
from .models import CollectionAction, CollectionCase
from .schemas import (
    ActionResponse,
    CaseActionRequest,
    CaseCreateRequest,
    CaseListResponse,
    CaseResponse,
    LoanEventRequest,
    PaymentEventRequest,
)

settings = get_settings()
assignment_service = AssignmentService(settings.collector_pool)
case_service = CaseService(assignment_service)
app = FastAPI(title='collection-svc', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/healthz')
def healthz() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.post('/collections/cases', response_model=CaseResponse, status_code=201)
def create_case(payload: CaseCreateRequest) -> CaseResponse:
    case = case_service.create_case(
        loan_id=payload.loanId,
        user_id=payload.userId,
        bucket=payload.bucket,
        principal_due=payload.principalDue,
        currency=payload.currency,
        assigned_to=payload.assignedTo,
        notes=payload.notes
    )
    return _to_case_response(case)


@app.get('/collections/cases', response_model=CaseListResponse)
def list_cases(
    bucket: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    assignedTo: Optional[str] = Query(default=None)
) -> CaseListResponse:
    cases = case_service.list_cases(bucket=bucket, status=status, assignee=assignedTo)
    return CaseListResponse(items=[_to_case_response(case) for case in cases])


@app.get('/collections/cases/{case_id}', response_model=CaseResponse)
def get_case(case_id: str = Path(...)) -> CaseResponse:
    case = case_service.get_case(case_id)
    return _to_case_response(case)


@app.post('/collections/cases/{case_id}/actions', response_model=ActionResponse, status_code=201)
def add_action(case_id: str, payload: CaseActionRequest) -> ActionResponse:
    action = case_service.record_action(
        case_id=case_id,
        action_type=payload.actionType,
        actor=payload.actor,
        note=payload.note,
        result=payload.result,
        status_after=payload.status,
        ptp_amount=payload.ptpAmount,
        ptp_due_at=payload.ptpDueAt
    )
    return _to_action_response(action)


@app.post('/events/loan', status_code=202)
def consume_loan_event(payload: LoanEventRequest) -> dict:
    case = case_service.sync_case_from_loan_event(
        loan_id=payload.loanId,
        user_id=payload.userId,
        bucket=payload.bucket,
        principal_due=payload.principalDue,
        currency=payload.currency,
        assigned_to=payload.assignedTo,
        notes=payload.notes
    )
    return {'status': 'accepted', 'caseId': case.case_id, 'eventType': payload.eventType}


@app.post('/events/payment', status_code=202)
def consume_payment_event(payload: PaymentEventRequest) -> dict:
    case = case_service.apply_payment_event(
        loan_id=payload.loanId,
        remaining_due=payload.remainingDue,
        event_type=payload.eventType,
        actor=payload.actor
    )
    return {'status': 'accepted', 'caseId': case.case_id if case else None, 'eventType': payload.eventType}


def _to_case_response(case: CollectionCase) -> CaseResponse:
    return CaseResponse(
        caseId=case.case_id,
        loanId=case.loan_id,
        userId=case.user_id,
        bucket=case.bucket,
        principalDue=case.principal_due,
        currency=case.currency,
        status=case.status,
        assignedTo=case.assigned_to,
        createdAt=case.created_at,
        updatedAt=case.updated_at,
        ptpAmount=case.ptp_amount,
        ptpDueAt=case.ptp_due_at,
        lastAction=case.last_action,
        notes=case.notes,
        actions=[_to_action_response(action) for action in case.actions],
    )


def _to_action_response(action: CollectionAction) -> ActionResponse:
    return ActionResponse(
        actionId=action.action_id,
        actionType=action.action_type,
        actor=action.actor,
        note=action.note,
        result=action.result,
        ptpAmount=action.ptp_amount,
        ptpDueAt=action.ptp_due_at,
        createdAt=action.created_at,
    )
