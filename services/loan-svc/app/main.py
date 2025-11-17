from typing import Optional

from fastapi import FastAPI, Query, Path, HTTPException, status
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .schemas import (
    ProductListResponse,
    LoanDraftRequest,
    LoanSubmitResponse,
    ContractResponse,
    RepaymentApplyRequest,
    RepaymentApplyResponse,
    LoanDetailResponse,
    RepaymentScheduleResponse,
    LoanListResponse,
)
from .service import filter_products, load_products
from .loan_service import LoanService
from .risk_client import evaluate
from .repository import get_application, list_applications_by_user
from .contract_service import generate_contract
from .billing_service import LoanBillingService
from .schedule_repository import get_schedule
from .models import LoanApplication

settings = get_settings()
app = FastAPI(title='loan-svc', version='0.2.0')
billing_service = LoanBillingService()
loan_service = LoanService(billing_service=billing_service)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/healthz')
def healthz() -> dict:
    try:
        load_products()
        status_msg = 'ok'
    except Exception as exc:
        status_msg = f'error: {exc}'
    return {'status': status_msg, 'service': settings.app_name}


@app.get('/loan/products', response_model=ProductListResponse)
def get_products(productId: Optional[str] = Query(default=None)) -> ProductListResponse:
    items = filter_products(productId)
    return ProductListResponse(items=items)


@app.post('/loans', response_model=LoanSubmitResponse, status_code=201)
def create_loan(payload: LoanDraftRequest) -> LoanSubmitResponse:
    app_model = loan_service.create_draft(payload.userId, payload.productId, payload.amount, payload.termDays)
    return LoanSubmitResponse(loanId=app_model.loan_id, status=app_model.status, decision=None, score=None)


@app.post('/loans/{loan_id}/submit', response_model=LoanSubmitResponse)
def submit_loan(loan_id: str = Path(...)) -> LoanSubmitResponse:
    app_model = loan_service.submit(loan_id)
    decision, score = evaluate(app_model.user_id, app_model.loan_id, app_model.requested_amount)
    app_model.score = score
    app_model.decision_reason = decision
    return LoanSubmitResponse(loanId=app_model.loan_id, status=app_model.status, decision=decision, score=score)


@app.get('/loans/{loan_id}/contracts', response_model=ContractResponse)
def get_contract(loan_id: str = Path(...)) -> ContractResponse:
    app_model = get_application(loan_id)
    if not app_model:
        raise HTTPException(status_code=404, detail='loan not found')
    contract = generate_contract(app_model)
    return ContractResponse(**contract)


@app.post('/loans/{loan_id}/repayments', response_model=RepaymentApplyResponse)
def apply_repayment(payload: RepaymentApplyRequest, loan_id: str = Path(...)) -> RepaymentApplyResponse:
    schedule, applied = billing_service.apply_repayment(
        loan_id=loan_id,
        amount=payload.amount,
        currency=payload.currency,
        paid_at=payload.paidAt
    )


@app.get('/loans/{loan_id}', response_model=LoanDetailResponse)
def get_loan_detail(loan_id: str = Path(...)) -> LoanDetailResponse:
    app_model = get_application(loan_id)
    if not app_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='loan not found')
    return LoanDetailResponse(
        loanId=app_model.loan_id,
        userId=app_model.user_id,
        productId=app_model.product_id,
        amount=app_model.requested_amount,
        termDays=app_model.term_days,
        status=app_model.status,
        decision=app_model.decision_reason,
        score=app_model.score,
        createdAt=app_model.created_at,
        updatedAt=app_model.updated_at,
    )


@app.get('/loans/{loan_id}/schedule', response_model=RepaymentScheduleResponse)
def get_schedule_view(loan_id: str = Path(...)) -> RepaymentScheduleResponse:
    schedule = get_schedule(loan_id)
    if not schedule:
        app_model = get_application(loan_id)
        if not app_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='loan not found')
        schedule = billing_service.ensure_schedule(app_model)
    return RepaymentScheduleResponse(
        loanId=schedule.loan_id,
        currency=schedule.currency,
        originalAmount=schedule.original_amount,
        outstandingAmount=schedule.outstanding_amount,
        paidAmount=schedule.paid_amount,
        status=schedule.status,
        lastPaidAt=schedule.last_paid_at,
        updatedAt=schedule.updated_at,
    )


@app.get('/users/{user_id}/loans', response_model=LoanListResponse)
def list_user_loans(
    user_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    status: Optional[str] = Query(default=None),
) -> LoanListResponse:
    loans = list_applications_by_user(user_id, limit=limit, status=status)
    items = [_loan_item_with_schedule(app_model) for app_model in loans]
    return LoanListResponse(items=items)


def _loan_item_with_schedule(app_model: LoanApplication) -> dict:
    schedule = get_schedule(app_model.loan_id)
    outstanding = schedule.outstanding_amount if schedule else 0
    original = schedule.original_amount if schedule else 0
    last_paid = schedule.last_paid_at if schedule else None
    return {
        'loanId': app_model.loan_id,
        'productId': app_model.product_id,
        'amount': app_model.requested_amount,
        'termDays': app_model.term_days,
        'status': app_model.status,
        'decision': app_model.decision_reason,
        'score': app_model.score,
        'createdAt': app_model.created_at,
        'updatedAt': app_model.updated_at,
        'outstandingAmount': outstanding,
        'originalAmount': original,
        'lastPaidAt': last_paid,
    }
    return RepaymentApplyResponse(
        loanId=loan_id,
        appliedAmount=applied,
        remainingDue=schedule.outstanding_amount,
        currency=schedule.currency,
        status=schedule.status,
        lastPaidAt=schedule.last_paid_at
    )
