from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_db
from .repository import upsert_device
from .schemas import DevicePayload, DeviceResponse

app = FastAPI(title='user-svc', version='0.1.0')
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def startup() -> None:
    init_db()


def mask_phone(user_id: str) -> str:
    if len(user_id) <= 4:
        return '***'
    return f"{user_id[:-4]}****"


@app.get('/healthz')
def healthz() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.put('/users/{user_id}/device', response_model=DeviceResponse)
async def put_device(
    payload: DevicePayload,
    user_id: str = Path(..., min_length=3, max_length=64)
) -> DeviceResponse:
    record = upsert_device(
        user_id,
        device_id=payload.deviceId,
        fingerprint=payload.fingerprint,
        platform=payload.platform,
        app_version=payload.appVersion,
        privacy_consent=payload.privacyConsent,
        location_consent=payload.locationConsent
    )
    return DeviceResponse(
        userId=record['user_id'],
        deviceId=record['device_id'],
        fingerprint=record['fingerprint'],
        platform=record['platform'],
        appVersion=record['app_version'],
        privacyConsent=bool(record['privacy_consent']),
        locationConsent=bool(record['location_consent']),
        lastActiveAt=record['last_active_at']
    )
