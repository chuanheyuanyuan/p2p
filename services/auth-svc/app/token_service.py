from datetime import datetime, timedelta

from fastapi import HTTPException, status
from jose import jwt

from .config import Settings
from .schemas import OTPRecord, TokenRequest, TokenResponse
from .storage import BaseBackend, delete_key, get_json
from .utils import hash_code


class TokenService:
    def __init__(self, backend: BaseBackend, settings: Settings) -> None:
        self.backend = backend
        self.settings = settings

    async def exchange(self, payload: TokenRequest) -> TokenResponse:
        key = self._otp_key(payload.requestId)
        data = await get_json(self.backend, key)
        if not data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='OTP 已失效或不存在')

        record = OTPRecord(**data)
        if record.expire_at < datetime.utcnow():
            await delete_key(self.backend, key)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='OTP 已过期')

        supplied_hash = hash_code(payload.otpCode, self.settings.otp_code_secret)
        if supplied_hash != record.code_hash:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='OTP 错误')

        await delete_key(self.backend, key)

        access_token = self._issue_token(
            subject=record.phone,
            scope='borrower',
            device_id=payload.deviceId,
            ttl=self.settings.jwt_access_ttl_seconds,
            token_type='access'
        )
        refresh_token = self._issue_token(
            subject=record.phone,
            scope='borrower',
            device_id=payload.deviceId,
            ttl=self.settings.jwt_refresh_ttl_seconds,
            token_type='refresh'
        )

        return TokenResponse(
            accessToken=access_token,
            refreshToken=refresh_token,
            expiresIn=self.settings.jwt_access_ttl_seconds
        )

    def _issue_token(self, subject: str, scope: str, device_id: str, ttl: int, token_type: str) -> str:
        now = datetime.utcnow()
        payload = {
            'sub': subject,
            'scope': scope,
            'deviceId': device_id,
            'type': token_type,
            'iat': now,
            'exp': now + timedelta(seconds=ttl)
        }
        return jwt.encode(payload, self.settings.jwt_secret, algorithm=self.settings.jwt_algorithm)

    def _otp_key(self, request_id: str) -> str:
        return f"otp:req:{request_id}"
