from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .dependencies import get_otp_service, get_token_service
from .schemas import OTPRequest, OTPResponse, TokenRequest, TokenResponse
from .service import OTPService
from .token_service import TokenService

app = FastAPI(title='auth-svc', version='0.1.0')
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/healthz')
async def healthz() -> dict:
    return {'status': 'ok'}


@app.post('/auth/otp', response_model=OTPResponse)
async def request_otp(payload: OTPRequest, service: OTPService = Depends(get_otp_service)) -> OTPResponse:
    return await service.issue(payload)


@app.post('/auth/token', response_model=TokenResponse)
async def exchange_token(payload: TokenRequest, service: TokenService = Depends(get_token_service)) -> TokenResponse:
    return await service.exchange(payload)
