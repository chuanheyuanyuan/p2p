import sqlite3
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List, Optional

from .config import Settings
from .models import AgingSummary, DailyMetricsRecord


class DailyMetricsCalculator:
    def __init__(self, settings: Settings):
        self.settings = settings

    def calculate(self, business_date: date) -> DailyMetricsRecord:
        day_str = business_date.isoformat()
        metrics: Dict[str, object] = {}
        notes: List[str] = []

        applications = self._count(
            self.settings.loan_db_path,
            'SELECT COUNT(*) FROM loan_applications WHERE DATE(created_at) = ?',
            (day_str,),
        )
        submitted = self._count(
            self.settings.loan_db_path,
            "SELECT COUNT(*) FROM loan_applications WHERE DATE(updated_at) = ? AND status != 'DRAFT'",
            (day_str,),
        )
        disbursements = self._count(
            self.settings.payment_db_path,
            "SELECT COUNT(*) FROM disbursements WHERE status = 'SUCCESS' AND DATE(updated_at) = ?",
            (day_str,),
        )
        disbursement_amount = self._sum_decimal(
            self.settings.payment_db_path,
            "SELECT amount FROM disbursements WHERE status = 'SUCCESS' AND DATE(updated_at) = ?",
            (day_str,),
        )
        repayments = self._count(
            self.settings.payment_db_path,
            "SELECT COUNT(*) FROM repayments WHERE status = 'POSTED' AND DATE(paid_at) = ?",
            (day_str,),
        )
        repayment_amount = self._sum_decimal(
            self.settings.payment_db_path,
            "SELECT applied_amount FROM repayments WHERE status = 'POSTED' AND DATE(paid_at) = ?",
            (day_str,),
        )
        cases_opened = self._count(
            self.settings.collection_db_path,
            'SELECT COUNT(*) FROM collection_cases WHERE DATE(created_at) = ?',
            (day_str,),
        )
        cases_closed = self._count(
            self.settings.collection_db_path,
            'SELECT COUNT(*) FROM collection_cases WHERE resolved_at IS NOT NULL AND DATE(resolved_at) = ?',
            (day_str,),
        )
        active_cases = self._count(
            self.settings.collection_db_path,
            "SELECT COUNT(*) FROM collection_cases WHERE status NOT IN ('PAID', 'WRITE_OFF')",
        )
        bucket_breakdown = self._bucket_breakdown()

        metrics.update(
            {
                'applications': applications,
                'submittedApplications': submitted,
                'disbursements': disbursements,
                'disbursementAmount': self._format_decimal(disbursement_amount),
                'repayments': repayments,
                'repaymentAmount': self._format_decimal(repayment_amount),
                'casesOpened': cases_opened,
                'casesClosed': cases_closed,
                'activeCases': active_cases,
                'bucketBreakdown': bucket_breakdown.by_bucket,
            }
        )

        missing_metrics = []
        if not self.settings.loan_db_path.exists():
            notes.append('loan.db 未找到，贷款相关指标默认为 0')
        if not self.settings.payment_db_path.exists():
            notes.append('payment.db 未找到，放款/还款指标默认为 0')
        if not self.settings.collection_db_path.exists():
            notes.append('collection.db 未找到，催收指标默认为 0')
        if applications == 0:
            missing_metrics.append('applications')
        if disbursements == 0 and disbursement_amount == Decimal('0'):
            missing_metrics.append('disbursementAmount')
        metrics['missingMetrics'] = missing_metrics
        metrics['sources'] = self._sources_status()

        return DailyMetricsRecord(
            business_date=day_str,
            currency=self.settings.default_currency,
            metrics=metrics,
            notes=notes,
            generated_at=datetime.utcnow(),
        )

    def aging_summary(self, bucket: Optional[str] = None) -> AgingSummary:
        connection_path = self.settings.collection_db_path
        by_bucket: Dict[str, int] = {}
        by_status: Dict[str, int] = {}
        total = 0
        if connection_path.exists():
            with sqlite3.connect(connection_path, check_same_thread=False) as conn:
                conn.row_factory = sqlite3.Row
                if bucket:
                    rows = conn.execute(
                        'SELECT status, COUNT(*) as total FROM collection_cases WHERE bucket = ? GROUP BY status',
                        (bucket,),
                    ).fetchall()
                    total = sum(row['total'] for row in rows)
                    by_status = {row['status']: row['total'] for row in rows}
                    bucket_rows = conn.execute(
                        'SELECT bucket, COUNT(*) as total FROM collection_cases WHERE bucket = ? GROUP BY bucket',
                        (bucket,),
                    ).fetchall()
                    by_bucket = {row['bucket']: row['total'] for row in bucket_rows}
                else:
                    rows = conn.execute(
                        'SELECT bucket, COUNT(*) as total FROM collection_cases GROUP BY bucket',
                    ).fetchall()
                    by_bucket = {row['bucket']: row['total'] for row in rows}
                    total = sum(by_bucket.values())
                    status_rows = conn.execute(
                        'SELECT status, COUNT(*) as total FROM collection_cases GROUP BY status',
                    ).fetchall()
                    by_status = {row['status']: row['total'] for row in status_rows}
        else:
            by_bucket = {}
            by_status = {}
            total = 0
        summary_bucket = bucket or 'ALL'
        return AgingSummary(
            bucket=summary_bucket,
            total_cases=total,
            by_status=by_status,
            by_bucket=by_bucket,
            generated_at=datetime.utcnow(),
        )

    def _count(self, db_path: Path, query: str, params: Optional[tuple] = None) -> int:
        if not db_path.exists():
            return 0
        params = params or tuple()
        with sqlite3.connect(db_path, check_same_thread=False) as conn:
            row = conn.execute(query, params).fetchone()
            if not row:
                return 0
            value = row[0]
        return int(value or 0)

    def _sum_decimal(self, db_path: Path, query: str, params: Optional[tuple] = None) -> Decimal:
        if not db_path.exists():
            return Decimal('0')
        total = Decimal('0')
        params = params or tuple()
        with sqlite3.connect(db_path, check_same_thread=False) as conn:
            for row in conn.execute(query, params).fetchall():
                raw = row[0]
                if raw is None:
                    continue
                total += Decimal(str(raw))
        return total

    def _bucket_breakdown(self) -> AgingSummary:
        return self.aging_summary(None)

    def _format_decimal(self, value: Decimal) -> str:
        return str(value.quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP))

    def _sources_status(self) -> Dict[str, bool]:
        return {
            'loanDb': self.settings.loan_db_path.exists(),
            'paymentDb': self.settings.payment_db_path.exists(),
            'collectionDb': self.settings.collection_db_path.exists(),
            'ledgerDb': self.settings.ledger_db_path.exists(),
        }
