from datetime import datetime
from typing import Optional

from .database import get_conn


def upsert_device(
    user_id: str,
    *,
    device_id: str,
    fingerprint: str,
    platform: str,
    app_version: str,
    privacy_consent: bool,
    location_consent: bool
) -> dict:
    now_iso = datetime.utcnow().isoformat()
    sql = (
        "INSERT INTO user_devices (user_id, device_id, fingerprint, platform, app_version, privacy_consent, location_consent, last_active_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(user_id, fingerprint) DO UPDATE SET "
        "device_id=excluded.device_id, platform=excluded.platform, app_version=excluded.app_version, "
        "privacy_consent=excluded.privacy_consent, location_consent=excluded.location_consent, "
        "updated_at=datetime('now'), last_active_at=datetime('now')"
    )
    with get_conn() as conn:
        conn.execute(
            sql,
            (user_id, device_id, fingerprint, platform, app_version, int(privacy_consent), int(location_consent), now_iso)
        )
        row = conn.execute(
            "SELECT user_id, device_id, fingerprint, platform, app_version, privacy_consent, location_consent, last_active_at FROM user_devices WHERE user_id=? AND fingerprint=?",
            (user_id, fingerprint)
        ).fetchone()
        return dict(row)
