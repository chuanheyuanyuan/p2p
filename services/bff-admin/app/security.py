from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import AdminUser, Settings, get_settings

bearer_scheme = HTTPBearer(auto_error=False)


def issue_token(user: AdminUser, settings: Settings) -> str:
    now = datetime.utcnow()
    payload = {
        'sub': user.username,
        'userId': user.id,
        'name': user.displayName,
        'roles': user.roles,
        'permissions': user.permissions,
        'email': user.email,
        'title': user.title,
        'iat': now,
        'exp': now + timedelta(seconds=settings.session_ttl_seconds),
        'scope': 'admin',
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str, settings: Settings) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='token 无效') from exc


def get_current_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='缺少 Authorization 头')
    payload = decode_token(credentials.credentials, settings)
    if payload.get('scope') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='无访问权限')
    return payload
