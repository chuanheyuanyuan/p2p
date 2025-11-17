from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import AdminUser, Settings, get_settings
from ..schemas import LoginRequest, LoginResponse, SessionUser
from ..security import get_current_admin, issue_token

router = APIRouter(prefix='/admin/v1/auth', tags=['AdminAuth'])


def _find_user(settings: Settings, username: str) -> AdminUser:
    for user in settings.admin_users:
        if user.username == username:
            return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='账号或密码错误')


@router.post('/login', response_model=LoginResponse)
def login(payload: LoginRequest, settings: Settings = Depends(get_settings)) -> LoginResponse:
    user = _find_user(settings, payload.username)
    if payload.password != user.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='账号或密码错误')
    token = issue_token(user, settings)
    return _build_session(user, token, settings.session_ttl_seconds)


@router.get('/me', response_model=LoginResponse)
def current_session(
    principal: dict = Depends(get_current_admin),
    settings: Settings = Depends(get_settings),
) -> LoginResponse:
    username = principal.get('sub')
    user = _find_user(settings, username)
    token = issue_token(user, settings)
    return _build_session(user, token, settings.session_ttl_seconds)


def _build_session(user: AdminUser, token: str, ttl: int) -> LoginResponse:
    session_user = SessionUser(id=user.id, name=user.displayName, email=user.email, title=user.title)
    return LoginResponse(
        accessToken=token,
        refreshToken=token,
        expiresIn=ttl,
        user=session_user,
        roles=user.roles,
        permissions=user.permissions or ['applications:read'],
    )
