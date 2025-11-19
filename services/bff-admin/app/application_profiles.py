from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import List

from .config import Settings

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS application_profiles (
    loan_id TEXT PRIMARY KEY,
    phone TEXT,
    channel TEXT,
    reviewer TEXT,
    tags_json TEXT,
    documents_json TEXT,
    is_repeat INTEGER DEFAULT 0,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

PROFILE_FIXTURES = [
    {
        'loan_id': 'LN123',
        'phone': '+233-5500-1123',
        'channel': 'Google Ads',
        'reviewer': '资深审批员',
        'is_repeat': 1,
        'tags': ['复借', '高评分'],
        'documents': [
            {
                'type': 'ID',
                'name': '身份证OCR',
                'url': 'https://static.local/docs/LN123/id_ocr.pdf',
                'updatedAt': '2024-05-12T09:30:00',
            },
            {
                'type': 'CONTRACT',
                'name': '借款合同',
                'url': 'https://static.local/docs/LN123/contract.pdf',
                'updatedAt': '2024-05-12T09:35:00',
            },
        ],
    },
    {
        'loan_id': 'LN124',
        'phone': '+233-5500-2124',
        'channel': 'Affiliate',
        'reviewer': '系统',
        'is_repeat': 1,
        'tags': ['老户', '正常'],
        'documents': [
            {
                'type': 'KYC',
                'name': '人脸识别',
                'url': 'https://static.local/docs/LN124/face.png',
                'updatedAt': '2024-05-05T08:00:00',
            }
        ],
    },
    {
        'loan_id': 'LN777',
        'phone': '+233-5599-7777',
        'channel': 'App Organic',
        'reviewer': '新户审批员',
        'is_repeat': 0,
        'tags': ['新户', '需跟进'],
        'documents': [
            {
                'type': 'OCR',
                'name': '护照扫描',
                'url': 'https://static.local/docs/LN777/passport.pdf',
                'updatedAt': '2024-04-01T12:00:00',
            }
        ],
    },
]


def ensure_application_profiles(settings: Settings) -> None:
    settings.admin_db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.admin_db_path)
    try:
        conn.execute(CREATE_SQL)
        _seed_profiles(conn, PROFILE_FIXTURES)
        conn.commit()
    finally:
        conn.close()


def _seed_profiles(conn: sqlite3.Connection, fixtures: List[dict]) -> None:
    now = datetime.utcnow().isoformat()
    for item in fixtures:
        tags_json = json.dumps(item.get('tags', []), ensure_ascii=False)
        documents_json = json.dumps(item.get('documents', []), ensure_ascii=False)
        conn.execute(
            """
            INSERT INTO application_profiles (loan_id, phone, channel, reviewer, tags_json, documents_json, is_repeat, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(loan_id) DO UPDATE SET
                phone=excluded.phone,
                channel=excluded.channel,
                reviewer=excluded.reviewer,
                tags_json=excluded.tags_json,
                documents_json=excluded.documents_json,
                is_repeat=excluded.is_repeat,
                updated_at=excluded.updated_at
            """,
            (
                item['loan_id'],
                item.get('phone'),
                item.get('channel'),
                item.get('reviewer'),
                tags_json,
                documents_json,
                int(bool(item.get('is_repeat'))),
                now,
            ),
        )
