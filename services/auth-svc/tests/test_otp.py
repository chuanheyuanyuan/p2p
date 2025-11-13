import asyncio
from datetime import datetime
from pathlib import Path
import sys
from typing import List, Optional

import pytest
from fastapi import HTTPException

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import Settings
from app.provider import OTPProvider
from app.ratelimit import RateLimiter
from app.schemas import OTPRequest
from app.service import OTPService
from app.storage import InMemoryBackend, get_json


class DummyProvider(OTPProvider):
    def __init__(self) -> None:
        super().__init__()
        self.sent_messages: list[dict[str, str]] = []

    async def send(self, phone: str, country_code: str, channel: str, code: str) -> None:  # type: ignore[override]
        self.sent_messages.append(
            {
                'phone': phone,
                'countryCode': country_code,
                'channel': channel,
                'code': code,
            }
        )


def build_service(
    *,
    otp_limit: int = 3,
    allowed_channels: Optional[List[str]] = None,
) -> tuple[OTPService, DummyProvider, InMemoryBackend, Settings]:
    backend = InMemoryBackend()
    settings = Settings(
        redis_url=None,
        otp_rate_limit_count=otp_limit,
        otp_rate_limit_window_seconds=60,
        otp_allowed_channels=allowed_channels or ['sms'],
        otp_ttl_seconds=60,
        otp_code_secret='unit-test-secret',
        jwt_secret='unit-test-jwt',
    )
    limiter = RateLimiter(backend, settings.otp_rate_limit_count, settings.otp_rate_limit_window_seconds)
    provider = DummyProvider()
    service = OTPService(backend, limiter, provider, settings)
    return service, provider, backend, settings


def test_issue_success(monkeypatch):
    service, provider, backend, settings = build_service()
    monkeypatch.setattr('app.service.generate_code', lambda *args, **kwargs: '123456')

    payload = OTPRequest(phone='233555000111', countryCode='+233', channel='sms')
    response = asyncio.run(service.issue(payload))

    assert response.requestId
    ttl_delta = response.expireAt - datetime.utcnow()
    assert 0 < ttl_delta.total_seconds() <= settings.otp_ttl_seconds + 1

    assert provider.sent_messages == [
        {
            'phone': '233555000111',
            'countryCode': '+233',
            'channel': 'sms',
            'code': '123456',
        }
    ]

    stored = asyncio.run(get_json(backend, f"otp:req:{response.requestId}"))
    assert stored is not None
    assert stored['phone'] == '233555000111'
    assert stored['country_code'] == '+233'
    assert stored['channel'] == 'sms'
    assert stored['code_hash'] != '123456'


def test_rate_limit(monkeypatch):
    service, provider, _, _ = build_service(otp_limit=1)
    monkeypatch.setattr('app.service.generate_code', lambda *args, **kwargs: '999999')

    payload = OTPRequest(phone='1555000111', countryCode='+1', channel='sms')
    asyncio.run(service.issue(payload))

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(service.issue(payload))

    assert excinfo.value.status_code == 429
    assert len(provider.sent_messages) == 1


def test_rejects_unsupported_channel():
    service, _, _, _ = build_service(allowed_channels=['sms'])
    payload = OTPRequest(phone='447000111222', countryCode='+44', channel='email')

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(service.issue(payload))

    assert excinfo.value.status_code == 400
    assert 'channel' in excinfo.value.detail
