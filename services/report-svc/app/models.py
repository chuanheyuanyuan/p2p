from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class DailyMetricsRecord:
    business_date: str
    currency: str
    metrics: Dict[str, Any]
    notes: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgingSummary:
    bucket: str
    total_cases: int
    by_status: Dict[str, int]
    by_bucket: Dict[str, int]
    generated_at: datetime = field(default_factory=datetime.utcnow)
