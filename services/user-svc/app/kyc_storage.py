from pathlib import Path
import json
from fastapi.encoders import jsonable_encoder

from .config import get_settings

settings = get_settings()
KYC_DIR = settings.db_path.parent / 'kyc'
KYC_DIR.mkdir(parents=True, exist_ok=True)


def save_kyc_blob(user_id: str, data: dict) -> str:
    path = KYC_DIR / f"{user_id}.json"
    payload = jsonable_encoder(data)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(path)
