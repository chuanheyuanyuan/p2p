from datetime import datetime, date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .models import AgingSummary, DailyMetricsRecord


class DailyReportResponse(BaseModel):
    businessDate: date
    currency: str
    metrics: Dict[str, Any]
    notes: List[str] = Field(default_factory=list)
    generatedAt: datetime

    @classmethod
    def from_record(cls, record: DailyMetricsRecord) -> 'DailyReportResponse':
        return cls(
            businessDate=date.fromisoformat(record.business_date),
            currency=record.currency,
            metrics=record.metrics,
            notes=record.notes,
            generatedAt=record.generated_at,
        )


class AgingReportResponse(BaseModel):
    bucket: str
    totalCases: int
    byStatus: Dict[str, int]
    byBucket: Dict[str, int]
    generatedAt: datetime

    @classmethod
    def from_summary(cls, summary: AgingSummary) -> 'AgingReportResponse':
        return cls(
            bucket=summary.bucket,
            totalCases=summary.total_cases,
            byStatus=summary.by_status,
            byBucket=summary.by_bucket,
            generatedAt=summary.generated_at,
        )


class RecomputeResponse(BaseModel):
    refreshed: bool
    businessDate: date
    generatedAt: datetime
    currency: str
    missingMetrics: List[str] = Field(default_factory=list)

    @classmethod
    def from_record(cls, record: DailyMetricsRecord) -> 'RecomputeResponse':
        missing = record.metrics.get('missingMetrics', []) if record.metrics else []
        return cls(
            refreshed=True,
            businessDate=date.fromisoformat(record.business_date),
            generatedAt=record.generated_at,
            currency=record.currency,
            missingMetrics=missing,
        )
