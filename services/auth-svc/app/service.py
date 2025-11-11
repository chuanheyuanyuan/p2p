from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException, status

from .config import Settings
from .provider import OTPProvider
from .ratelimit import RateLimiter
from .schemas import OTPRecord, OTPRequest, OTPResponse
from .storage import BaseBackend, set_json
from .utils import generate_code, hash_code


class OTPService:
    def __init__(self, backend: BaseBackend, limiter: RateLimiter, provider: OTPProvider, settings: Settings) -> None:
        self.backend = backend
        self.limiter = limiter
        self.provider = provider
        self.settings = settings

    async def issue(self, payload: OTPRequest) -> OTPResponse:
        if payload.channel not in self.settings.otp_allowed_channels:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='channel not supported')

        await self.limiter.hit(self._rate_key(payload.phone))

        code = generate_code(self.settings.otp_code_length)
        request_id = uuid4().hex
        expire_at = datetime.utcnow() + timedelta(seconds=self.settings.otp_ttl_seconds)
        record = OTPRecord(
            request_id=request_id,
            phone=payload.phone,
            country_code=payload.countryCode,
            channel=payload.channel,
            code_hash=hash_code(code, self.settings.otp_code_secret),
            expire_at=expire_at
        )

        await set_json(self.backend, self._otp_key(request_id), record.dict(), self.settings.otp_ttl_seconds)

        await self.provider.send(payload.phone, payload.countryCode, payload.channel, code)

        return OTPResponse(requestId=request_id, expireAt=expire_at)

    def _rate_key(self, phone: str) -> str:
        return f"otp:rate:{phone}"

    def _otp_key(self, request_id: str) -> str:
        return f"otp:req:{request_id}"
