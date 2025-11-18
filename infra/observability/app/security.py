from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt

from .config import Settings, get_settings


def verify_service_claims(
    authorization: str = Header(default='', alias='Authorization'),
    settings: Settings = Depends(get_settings)
) -> dict:
    if not authorization.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='missing bearer token')
    token = authorization.split(' ', 1)[1].strip()
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token') from exc
    return claims
