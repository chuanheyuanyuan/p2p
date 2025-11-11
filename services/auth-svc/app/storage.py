import asyncio
import json
import time
from typing import Any, Dict, Optional

from fastapi.encoders import jsonable_encoder

try:
    import redis.asyncio as redis
except ImportError:  # pragma: no cover
    redis = None


class BaseBackend:
    async def set(self, key: str, value: str, ttl: int) -> None:
        raise NotImplementedError

    async def get(self, key: str) -> Optional[str]:
        raise NotImplementedError

    async def incr(self, key: str, ttl: int) -> int:
        raise NotImplementedError

    async def delete(self, key: str) -> None:
        raise NotImplementedError


class RedisBackend(BaseBackend):
    def __init__(self, url: str) -> None:
        if not redis:
            raise RuntimeError('redis library not available')
        self.client = redis.from_url(url, encoding='utf-8', decode_responses=True)

    async def set(self, key: str, value: str, ttl: int) -> None:
        await self.client.set(key, value, ex=ttl)

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def incr(self, key: str, ttl: int) -> int:
        pipe = self.client.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl)
        results = await pipe.execute()
        return int(results[0])

    async def delete(self, key: str) -> None:
        await self.client.delete(key)


class InMemoryBackend(BaseBackend):
    def __init__(self) -> None:
        self._store: Dict[str, tuple[str, float]] = {}
        self._lock: asyncio.Lock | None = None

    def _ensure_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def set(self, key: str, value: str, ttl: int) -> None:
        async with self._ensure_lock():
            self._store[key] = (value, time.time() + ttl)

    async def get(self, key: str) -> Optional[str]:
        async with self._ensure_lock():
            value = self._store.get(key)
            if not value:
                return None
            payload, expire_at = value
            if expire_at < time.time():
                self._store.pop(key, None)
                return None
            return payload

    async def incr(self, key: str, ttl: int) -> int:
        async with self._ensure_lock():
            value = self._store.get(key)
            now = time.time()
            if not value or value[1] < now:
                count = 1
            else:
                count = int(value[0]) + 1
            self._store[key] = (str(count), now + ttl)
            return count

    async def delete(self, key: str) -> None:
        async with self._ensure_lock():
            self._store.pop(key, None)


def get_backend(redis_url: Optional[str]) -> BaseBackend:
    if redis_url:
        try:
            return RedisBackend(redis_url)
        except Exception as exc:  # pragma: no cover
            print(f"[auth-svc] Redis backend init failed: {exc}, fallback to in-memory")
    return InMemoryBackend()


async def set_json(backend: BaseBackend, key: str, data: Any, ttl: int) -> None:
    payload = jsonable_encoder(data)
    await backend.set(key, json.dumps(payload), ttl)


async def get_json(backend: BaseBackend, key: str) -> Optional[Dict[str, Any]]:
    raw = await backend.get(key)
    if not raw:
        return None
    return json.loads(raw)


async def delete_key(backend: BaseBackend, key: str) -> None:
    await backend.delete(key)
