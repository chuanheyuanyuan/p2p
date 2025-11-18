from fastapi import Request
from httpx import AsyncClient


def get_http_client(request: Request) -> AsyncClient:
    client = getattr(request.app.state, 'http_client', None)
    if client is None:
        raise RuntimeError('HTTP client is not initialized')
    return client
