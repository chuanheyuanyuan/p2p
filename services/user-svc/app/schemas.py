from datetime import datetime
from typing import Optional

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


class KycPayload(BaseModel):
    status: constr(min_length=4, max_length=32)
    docType: Optional[str] = None
    docNumber: Optional[str] = None
    selfieUrl: Optional[str] = None
    docFrontUrl: Optional[str] = None
    docBackUrl: Optional[str] = None
    meta: Optional[dict] = None
    reviewer: Optional[str] = None
    reviewedAt: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            'example': {
                'status': 'REVIEWING',
                'docType': 'ID_CARD',
                'docNumber': 'GHA-123456',
                'selfieUrl': 'https://s3/kyc/selfie.jpg',
                'docFrontUrl': 'https://s3/kyc/front.jpg',
                'docBackUrl': 'https://s3/kyc/back.jpg',
                'meta': {'ocrScore': 0.97},
                'reviewer': 'kyc-agent-1'
            }
        }


class KycResponse(BaseModel):
    userId: str
    status: str
    docType: Optional[str]
    docNumber: Optional[str]
    selfieUrl: Optional[str]
    docFrontUrl: Optional[str]
    docBackUrl: Optional[str]
    reviewer: Optional[str]
    reviewedAt: Optional[str]
    updatedAt: str
    metaPath: str
