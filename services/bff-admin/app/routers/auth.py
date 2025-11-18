from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..admin_store import get_admin_user, verify_admin_credentials
from ..config import AdminUser, Settings, get_settings
from ..schemas import LoginRequest, LoginResponse, SessionUser
from ..security import get_current_admin, issue_token

router = APIRouter(prefix='/admin/v1/auth', tags=['AdminAuth'])


@router.post('/login', response_model=LoginResponse)
def login(payload: LoginRequest, settings: Settings = Depends(get_settings)) -> LoginResponse:
    user = verify_admin_credentials(settings, payload.username, payload.password)
    token = issue_token(user, settings)
    return _build_session(user, token, settings.session_ttl_seconds)


@router.get('/me', response_model=LoginResponse)
def current_session(
    principal: dict = Depends(get_current_admin),
    settings: Settings = Depends(get_settings),
) -> LoginResponse:
    username = principal.get('sub')
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='token 缺少 subject')
    user = get_admin_user(settings, username)
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
