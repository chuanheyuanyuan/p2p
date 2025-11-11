from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .schemas import LedgerEntryRequest, LedgerEntryResponse
from .service import LedgerService

settings = get_settings()
app = FastAPI(title='ledger-svc', version='0.1.0')
service = LedgerService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/healthz')
def healthz() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.post('/ledger/entries', response_model=LedgerEntryResponse)
def post_entry(payload: LedgerEntryRequest) -> LedgerEntryResponse:
    return service.post_entry(payload)
