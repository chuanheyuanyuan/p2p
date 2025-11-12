import json
from datetime import datetime
from typing import Optional

from .database import get_connection
from .models import DailyMetricsRecord


def save_daily_metrics(record: DailyMetricsRecord) -> DailyMetricsRecord:
    record.generated_at = record.generated_at or datetime.utcnow()
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO daily_metrics (business_date, currency, metrics_json, notes_json, generated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(business_date) DO UPDATE SET
                currency=excluded.currency,
                metrics_json=excluded.metrics_json,
                notes_json=excluded.notes_json,
                generated_at=excluded.generated_at
            ''',
            (
                record.business_date,
                record.currency,
                json.dumps(record.metrics, ensure_ascii=False),
                json.dumps(record.notes, ensure_ascii=False),
                record.generated_at.isoformat(),
            ),
        )
        conn.commit()
    return record


def get_daily_metrics(business_date: str) -> Optional[DailyMetricsRecord]:
    with get_connection() as conn:
        row = conn.execute(
            'SELECT * FROM daily_metrics WHERE business_date = ?',
            (business_date,),
        ).fetchone()
    if not row:
        return None
    return DailyMetricsRecord(
        business_date=row['business_date'],
        currency=row['currency'],
        metrics=json.loads(row['metrics_json']),
        notes=json.loads(row['notes_json']),
        generated_at=datetime.fromisoformat(row['generated_at']),
    )
