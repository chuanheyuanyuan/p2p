from __future__ import annotations

import sqlite3
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, Optional

from .config import Settings


class MetricsCalculator:
    def __init__(self, settings: Settings):
        self.settings = settings

    def calculate(self, business_date: date) -> Dict[str, object]:
        ds = business_date.isoformat()
        metrics: Dict[str, object] = {}
        metrics['applications'] = self._count(
            self.settings.loan_db_path,
            'SELECT COUNT(*) FROM loan_applications WHERE DATE(created_at) = ?',
            (ds,),
        )
        metrics['submittedApplications'] = self._count(
            self.settings.loan_db_path,
            "SELECT COUNT(*) FROM loan_applications WHERE DATE(updated_at) = ? AND status != 'DRAFT'",
            (ds,),
        )
        metrics['disbursements'] = self._count(
            self.settings.payment_db_path,
            "SELECT COUNT(*) FROM disbursements WHERE status = 'SUCCESS' AND DATE(updated_at) = ?",
            (ds,),
        )
        metrics['disbursementAmount'] = self._format_decimal(
            self._sum_decimal(
                self.settings.payment_db_path,
                "SELECT amount FROM disbursements WHERE status = 'SUCCESS' AND DATE(updated_at) = ?",
                (ds,),
            )
        )
        metrics['repayments'] = self._count(
            self.settings.payment_db_path,
            "SELECT COUNT(*) FROM repayments WHERE status = 'POSTED' AND DATE(paid_at) = ?",
            (ds,),
        )
        metrics['repaymentAmount'] = self._format_decimal(
            self._sum_decimal(
                self.settings.payment_db_path,
                "SELECT applied_amount FROM repayments WHERE status = 'POSTED' AND DATE(paid_at) = ?",
                (ds,),
            )
        )
        metrics['casesOpened'] = self._count(
            self.settings.collection_db_path,
            'SELECT COUNT(*) FROM collection_cases WHERE DATE(created_at) = ?',
            (ds,),
        )
        metrics['casesClosed'] = self._count(
            self.settings.collection_db_path,
            'SELECT COUNT(*) FROM collection_cases WHERE resolved_at IS NOT NULL AND DATE(resolved_at) = ?',
            (ds,),
        )
        metrics['activeCases'] = self._count(
            self.settings.collection_db_path,
            "SELECT COUNT(*) FROM collection_cases WHERE status NOT IN ('PAID','WRITE_OFF')",
        )
        metrics['bucketBreakdown'] = self._bucket_breakdown()
        metrics['channelFunnel'] = self._channel_funnel(ds)
        metrics['generatedAt'] = datetime.utcnow().isoformat() + 'Z'
        return metrics

    def _bucket_breakdown(self) -> Dict[str, int]:
        path = self.settings.collection_db_path
        if not path.exists():
            return {}
        try:
            with sqlite3.connect(path, check_same_thread=False) as conn:
                rows = conn.execute('SELECT bucket, COUNT(*) as total FROM collection_cases GROUP BY bucket').fetchall()
        except sqlite3.Error:
            return {}
        return {row[0]: row[1] for row in rows}

    def _count(self, db_path: Path, query: str, params: Optional[tuple] = None) -> int:
        if not db_path.exists():
            return 0
        try:
            with sqlite3.connect(db_path, check_same_thread=False) as conn:
                row = conn.execute(query, params or tuple()).fetchone()
        except sqlite3.Error:
            return 0
        return int(row[0] or 0) if row else 0

    def _sum_decimal(self, db_path: Path, query: str, params: Optional[tuple] = None) -> Decimal:
        if not db_path.exists():
            return Decimal('0')
        total = Decimal('0')
        try:
            with sqlite3.connect(db_path, check_same_thread=False) as conn:
                for row in conn.execute(query, params or tuple()).fetchall():
                    value = row[0]
                    if value is None:
                        continue
                    total += Decimal(str(value))
        except sqlite3.Error:
            return Decimal('0')
        return total

    def _format_decimal(self, value: Decimal) -> str:
        return str(value.quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP))

    def _channel_funnel(self, business_day: str) -> list[dict]:
        """
        读取 channel.db 汇总单日漏斗，若库不存在则返回空列表。
        """
        path = self.settings.channel_db_path
        if not path.exists():
            return []
        sql = """
        SELECT
            channel,
            SUM(CASE WHEN event='install' THEN 1 ELSE 0 END) as installs,
            SUM(CASE WHEN event='register' THEN 1 ELSE 0 END) as registrations,
            SUM(CASE WHEN event='apply' THEN 1 ELSE 0 END) as applications,
            SUM(CASE WHEN event='disburse' THEN 1 ELSE 0 END) as disbursements,
            SUM(CASE WHEN event='install' THEN cost ELSE 0 END) as spend
        FROM channel_attributions
        WHERE DATE(occurred_at) = ?
        GROUP BY channel
        ORDER BY channel
        """
        rows: list[dict] = []
        try:
            with sqlite3.connect(path, check_same_thread=False) as conn:
                conn.row_factory = sqlite3.Row
                for row in conn.execute(sql, (business_day,)).fetchall():
                    rows.append(
                        {
                            'channel': row['channel'],
                            'installs': row['installs'],
                            'registrations': row['registrations'],
                            'applications': row['applications'],
                            'disbursements': row['disbursements'],
                            'spend': self._format_decimal(Decimal(str(row['spend'] or 0))),
                        }
                    )
        except sqlite3.Error:
            return []
        return rows
