from fastapi import HTTPException, status

from .storage import BaseBackend


class RateLimiter:
    def __init__(self, backend: BaseBackend, limit: int, window_seconds: int) -> None:
        self.backend = backend
        self.limit = limit
        self.window = window_seconds

    async def hit(self, key: str) -> None:
        count = await self.backend.incr(key, self.window)
        if count > self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail='OTP 请求过于频繁，请稍后再试'
            )
