from datetime import datetime
from pydantic import BaseModel, Field, constr


class OTPRequest(BaseModel):
    phone: constr(min_length=6, max_length=20)
    countryCode: constr(min_length=1, max_length=5)
    channel: constr(min_length=2, max_length=20)

    class Config:
        json_schema_extra = {
            'example': {
                'phone': '233555000111',
                'countryCode': '+233',
                'channel': 'sms'
            }
        }


class OTPResponse(BaseModel):
    requestId: str
    expireAt: datetime


class OTPRecord(BaseModel):
    request_id: str
    phone: str
    country_code: str
    channel: str
    code_hash: str
    expire_at: datetime


class TokenRequest(BaseModel):
    requestId: str
    otpCode: constr(min_length=4, max_length=10)
    deviceId: constr(min_length=3, max_length=64)


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    expiresIn: int
