from datetime import datetime
from pydantic import BaseModel, Field, constr


class DevicePayload(BaseModel):
    deviceId: constr(min_length=3, max_length=64)
    fingerprint: constr(min_length=6, max_length=255)
    platform: constr(min_length=2, max_length=32)
    appVersion: constr(min_length=1, max_length=32)
    privacyConsent: bool = Field(default=False)
    locationConsent: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            'example': {
                'deviceId': 'device-abc',
                'fingerprint': 'fp-123456',
                'platform': 'android',
                'appVersion': '1.0.17',
                'privacyConsent': True,
                'locationConsent': False
            }
        }


class DeviceResponse(BaseModel):
    userId: str
    deviceId: str
    fingerprint: str
    platform: str
    appVersion: str
    privacyConsent: bool
    locationConsent: bool
    lastActiveAt: datetime
