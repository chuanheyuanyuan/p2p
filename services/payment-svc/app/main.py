from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .schemas import (
    DisbursementRequest,
    DisbursementResponse,
    CallbackPayload,
    RepaymentRequest,
    RepaymentResponse,
)
from .models import Disbursement, Repayment
from .repository import (
    save_disbursement,
    get_disbursement,
    list_disbursements,
    save_repayment,
    get_repayment_by_txn,
    list_repayments,
)
from .channel_client import send_to_channel
from .loan_client import post_repayment_to_loan_svc

settings = get_settings()
app = FastAPI(title='payment-svc', version='0.2.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/healthz')
def healthz() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.post('/payments/disbursements', response_model=DisbursementResponse, status_code=202)
def create_disbursement(payload: DisbursementRequest) -> DisbursementResponse:
    req_no = uuid4().hex
    disb = Disbursement(
        req_no=req_no,
        loan_id=payload.loanId,
        amount=payload.amount,
        account=payload.account.dict(),
        channel=payload.channel
    )
    save_disbursement(disb)
    send_to_channel(disb)
    return DisbursementResponse(reqNo=req_no, status=disb.status)


@app.post('/payments/repayments', response_model=RepaymentResponse, status_code=201)
def post_repayment(payload: RepaymentRequest) -> RepaymentResponse:
    existing = get_repayment_by_txn(payload.txnRef)
    if existing:
        return _build_repayment_response(existing)

    repayment = Repayment(
        repayment_id=uuid4().hex,
        loan_id=payload.loanId,
        amount=payload.amount,
        currency=payload.currency,
        channel=payload.channel,
        txn_ref=payload.txnRef,
        paid_at=payload.paidAt or datetime.utcnow()
    )

    schedule_view = post_repayment_to_loan_svc(
        loan_id=payload.loanId,
        amount=payload.amount,
        currency=payload.currency,
        paid_at=payload.paidAt
    )
    repayment.applied_amount = _decimal_from_payload(schedule_view, 'appliedAmount')
    repayment.remaining_due = _decimal_from_payload(schedule_view, 'remainingDue')
    save_repayment(repayment)
    _emit_repayment_posted(repayment)
    return _build_repayment_response(repayment)


@app.post('/callbacks/mock-channel')
def callback(payload: CallbackPayload) -> dict:
    disb = get_disbursement(payload.reqNo)
    if not disb:
        raise HTTPException(status_code=404, detail='reqNo not found')
    disb.status = payload.status
    disb.failure_reason = payload.failureReason
    save_disbursement(disb)
    return {'status': 'ack'}


@app.get('/payments/disbursements')
def list_disbs() -> list[dict]:
    return [
        {
            'reqNo': d.req_no,
            'loanId': d.loan_id,
            'status': d.status,
            'failureReason': d.failure_reason
        }
        for d in list_disbursements()
    ]


@app.get('/payments/repayments')
def list_repayment_records() -> list[dict]:
    return [
        {
            'repaymentId': r.repayment_id,
            'loanId': r.loan_id,
            'amount': str(r.amount),
            'appliedAmount': str(r.applied_amount),
            'remainingDue': str(r.remaining_due),
            'status': r.status,
            'txnRef': r.txn_ref,
            'paidAt': r.paid_at.isoformat() + 'Z'
        }
        for r in list_repayments()
    ]


def _decimal_from_payload(payload: dict, key: str) -> Decimal:
    value = payload.get(key)
    if value is None:
        return Decimal('0')
    return Decimal(str(value))


def _build_repayment_response(rep: Repayment) -> RepaymentResponse:
    return RepaymentResponse(
        repaymentId=rep.repayment_id,
        loanId=rep.loan_id,
        status=rep.status,
        appliedAmount=rep.applied_amount,
        remainingDue=rep.remaining_due,
        currency=rep.currency,
        txnRef=rep.txn_ref,
        paidAt=rep.paid_at
    )


def _emit_repayment_posted(rep: Repayment) -> None:
    print(
        'event=REPAYMENT_POSTED',
        f"loanId={rep.loan_id}",
        f"repaymentId={rep.repayment_id}",
        f"amount={rep.applied_amount}",
        f"remainingDue={rep.remaining_due}",
        f"txnRef={rep.txn_ref}",
        f"status={rep.status}"
    )
