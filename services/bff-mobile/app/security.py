from typing import Optional

from fastapi import Header, HTTPException, status
from pydantic import BaseModel


class BorrowerContext(BaseModel):
    userId: str
    deviceId: Optional[str] = None


async def get_borrower_context(
    x_user_id: Optional[str] = Header(default=None, alias='X-User-Id'),
    x_device_id: Optional[str] = Header(default=None, alias='X-Device-Id')
) -> BorrowerContext:
    if not x_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='缺少 X-User-Id 请求头')
    return BorrowerContext(userId=x_user_id, deviceId=x_device_id)
