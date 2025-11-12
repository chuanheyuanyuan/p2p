from datetime import date

from fastapi import FastAPI, Query
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .metrics_calculator import DailyMetricsCalculator
from .repository import get_daily_metrics, save_daily_metrics
from .schemas import AgingReportResponse, DailyReportResponse, RecomputeResponse

settings = get_settings()
app = FastAPI(title=settings.app_name, version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

calculator = DailyMetricsCalculator(settings)


@app.get('/healthz')
def healthz() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.get('/reports/daily', response_model=DailyReportResponse)
def get_daily_report(
    business_date: date = Query(..., alias='businessDate'),
    force_refresh: bool = Query(False, alias='forceRefresh'),
) -> DailyReportResponse:
    day_str = business_date.isoformat()
    record = get_daily_metrics(day_str)
    if record is None or force_refresh:
        record = calculator.calculate(business_date)
        save_daily_metrics(record)
    return DailyReportResponse.from_record(record)


@app.post('/reports/daily/refresh', response_model=RecomputeResponse)
def refresh_daily_report(business_date: date = Query(..., alias='businessDate')) -> RecomputeResponse:
    record = calculator.calculate(business_date)
    save_daily_metrics(record)
    return RecomputeResponse.from_record(record)


@app.get('/reports/aging', response_model=AgingReportResponse)
def get_aging_report(bucket: Optional[str] = Query(default=None)) -> AgingReportResponse:
    summary = calculator.aging_summary(bucket)
    return AgingReportResponse.from_summary(summary)
