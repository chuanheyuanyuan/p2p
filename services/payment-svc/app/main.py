from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .schemas import DisbursementRequest, DisbursementResponse, CallbackPayload
from .models import Disbursement
from .repository import save_disbursement, get_disbursement, list_disbursements
from .channel_client import send_to_channel

settings = get_settings()
app = FastAPI(title='payment-svc', version='0.1.0')

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
