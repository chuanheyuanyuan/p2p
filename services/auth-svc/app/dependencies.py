from fastapi import Depends

from .config import Settings, get_settings
from .provider import OTPProvider
from .ratelimit import RateLimiter
from .service import OTPService
from .token_service import TokenService
from .storage import BaseBackend, get_backend


def get_backend_dep(settings: Settings = Depends(get_settings)) -> BaseBackend:
    return get_backend(settings.redis_url)


def get_rate_limiter(
    backend: BaseBackend = Depends(get_backend_dep),
    settings: Settings = Depends(get_settings)
) -> RateLimiter:
    return RateLimiter(backend, settings.otp_rate_limit_count, settings.otp_rate_limit_window_seconds)


def get_provider() -> OTPProvider:
    return OTPProvider()


def get_otp_service(
    backend: BaseBackend = Depends(get_backend_dep),
    limiter: RateLimiter = Depends(get_rate_limiter),
    provider: OTPProvider = Depends(get_provider),
    settings: Settings = Depends(get_settings)
) -> OTPService:
    return OTPService(backend, limiter, provider, settings)


def get_token_service(
    backend: BaseBackend = Depends(get_backend_dep),
    settings: Settings = Depends(get_settings)
) -> TokenService:
    return TokenService(backend, settings)
