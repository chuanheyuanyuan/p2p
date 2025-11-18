from fastapi import HTTPException, status
from httpx import HTTPStatusError, RequestError


def build_service_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def translate_http_error(error: Exception) -> None:
    if isinstance(error, HTTPStatusError):
        detail = None
        try:
            detail = error.response.json()
        except ValueError:
            detail = error.response.text
        message = detail or error.response.reason_phrase or '下游服务返回错误'
        raise HTTPException(status_code=error.response.status_code, detail=message) from error
    if isinstance(error, RequestError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'下游服务不可达: {error}',
        ) from error
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='未知错误')
