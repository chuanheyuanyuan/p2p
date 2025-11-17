from __future__ import annotations

from typing import Any, Mapping, Optional

import httpx
from fastapi import HTTPException, status


async def forward_json(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    payload: Optional[Mapping[str, Any]] = None,
    headers: Optional[Mapping[str, str]] = None,
    params: Optional[Mapping[str, Any]] = None,
    service_name: str,
) -> Any:
    try:
        response = await client.request(method, url, json=payload, headers=headers, params=params)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f'{service_name} 暂不可用',
        ) from exc

    content_type = response.headers.get('content-type', '')
    if response.is_error:
        detail: Any
        if 'application/json' in content_type:
            try:
                body = response.json()
                detail = body.get('detail', body)
            except ValueError:
                detail = response.text or f'{service_name} 内部错误'
        else:
            detail = response.text or f'{service_name} 响应异常'
        raise HTTPException(status_code=response.status_code, detail=detail)

    if 'application/json' not in content_type:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f'{service_name} 返回非 JSON')

    try:
        return response.json()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f'{service_name} JSON 解析失败') from exc

