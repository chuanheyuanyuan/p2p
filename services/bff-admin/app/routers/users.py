from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import Settings, get_settings
from ..data_access import get_user_profile
from ..schemas import UserProfile
from ..security import get_current_admin

router = APIRouter(prefix='/admin/v1', tags=['Users'], dependencies=[Depends(get_current_admin)])


@router.get('/users/{user_id}', response_model=UserProfile)
def get_user(user_id: str, settings: Settings = Depends(get_settings)) -> UserProfile:
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='userId 必填')
    data = get_user_profile(settings, user_id)
    return UserProfile(**data)
