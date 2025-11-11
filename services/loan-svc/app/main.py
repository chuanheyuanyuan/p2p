from typing import Optional

from fastapi import FastAPI, Query, Path
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .schemas import ProductListResponse, LoanDraftRequest, LoanSubmitResponse
from .service import filter_products, load_products
from .loan_service import LoanService
from .risk_client import evaluate

settings = get_settings()
app = FastAPI(title='loan-svc', version='0.2.0')
loan_service = LoanService()

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
