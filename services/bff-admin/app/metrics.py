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
