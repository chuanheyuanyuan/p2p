from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from ..config import Settings, get_settings
from ..metrics import MetricsCalculator
from ..security import get_current_admin
from ..schemas import (
    DashboardConversion,
    DashboardKpi,
    DashboardOverdue,
    DashboardRecovery,
    DashboardStats,
    DashboardToday,
    ChannelFunnelRow,
    DailyStat,
    PaginatedDailyStats,
    ReportCenterResponse,
    ReportSummaryItem,
    OverdueMigrationRow,
    ReborrowRateRow,
)

router = APIRouter(prefix='/admin/v1', tags=['Reports'], dependencies=[Depends(get_current_admin)])


@router.get('/dashboard', response_model=DashboardStats)
def dashboard(settings: Settings = Depends(get_settings)) -> DashboardStats:
    calculator = MetricsCalculator(settings)
    metrics = calculator.calculate(date.today())
    disb_amount = Decimal(metrics['disbursementAmount']) if metrics.get('disbursementAmount') else Decimal('0')
    repayment_amount = Decimal(metrics['repaymentAmount']) if metrics.get('repaymentAmount') else Decimal('0')
    kpis = [
        DashboardKpi(label='今日放款金额', value=f"₵{disb_amount:,.0f}", delta='--'),
        DashboardKpi(label='今日申请笔数', value=str(metrics['applications']), delta='--'),
        DashboardKpi(label='今日还款金额', value=f"₵{repayment_amount:,.0f}", delta='--'),
    ]
    numerator = metrics['submittedApplications']
    denominator = max(metrics['applications'], 1)
    conversion_percent = round((numerator / denominator) * 100, 2)
    overdue_rate = _calc_overdue_rate(metrics['activeCases'], denominator)
    overdue = DashboardOverdue(
        rate=overdue_rate,
        dueToday=int(metrics['casesOpened']),
        repaid=int(metrics['casesClosed']),
        yesterdayRate=max(0.0, overdue_rate - 5),
        progress=min(100.0, metrics['repayments'] * 5.0),
    )
    recovery = DashboardRecovery(cases=int(metrics['activeCases']), assigned=int(metrics['casesOpened']), note='自动分案中')
    channel_funnel = [ChannelFunnelRow(**row) for row in metrics.get('channelFunnel', [])]
    installs = sum(item.installs for item in channel_funnel)
    regs = sum(item.registrations for item in channel_funnel)
    today_metrics = DashboardToday(
        installs=installs,
        regs=regs,
        logins=0,
        applies=int(metrics['applications']),
        disburses=int(metrics['disbursements']),
        repayments=int(metrics['repayments']),
    )
    conversion = DashboardConversion(percent=conversion_percent, numerator=int(numerator), denominator=int(denominator))
    return DashboardStats(
        kpis=kpis,
        overdue=overdue,
        recovery=recovery,
        today=today_metrics,
        conversion=conversion,
        channelFunnel=channel_funnel,
    )


@router.get('/reports/daily', response_model=PaginatedDailyStats)
def daily_stats(
    startDate: Optional[str] = Query(default=None),
    endDate: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1, le=200),
    pageSize: int = Query(default=30, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> PaginatedDailyStats:
    end_day = _parse_date(endDate) or date.today()
    start_day = _parse_date(startDate) or (end_day - timedelta(days=6))
    if start_day > end_day:
        start_day, end_day = end_day, start_day
    calculator = MetricsCalculator(settings)
    current = start_day
    rows: List[DailyStat] = []
    while current <= end_day:
        metrics = calculator.calculate(current)
        disb_amount = float(Decimal(metrics['disbursementAmount']) if metrics.get('disbursementAmount') else Decimal('0'))
        rows.append(
            DailyStat(
                date=current,
                installs=0,
                regs=0,
                logins=0,
                applies=int(metrics['applications']),
                disburses=int(metrics['disbursements']),
                repayments=int(metrics['repayments']),
                amount=disb_amount,
            )
        )
        current += timedelta(days=1)
    rows.sort(key=lambda item: item.date, reverse=True)
    total = len(rows)
    start_index = (page - 1) * pageSize
    end_index = start_index + pageSize
    page_items = rows[start_index:end_index]
    return PaginatedDailyStats(list=page_items, total=total)


@router.post('/reports/daily/export')
def export_daily() -> dict:
    return {'taskId': f'daily-export-{int(datetime.utcnow().timestamp())}'}


@router.get('/reports/center', response_model=ReportCenterResponse)
def report_center(
    businessDate: Optional[str] = Query(default=None),
    channel: Optional[str] = Query(default=None),
    product: Optional[str] = Query(default=None),
    settings: Settings = Depends(get_settings),
) -> ReportCenterResponse:
    target_date = _parse_date(businessDate) or date.today()
    calculator = MetricsCalculator(settings)
    metrics = calculator.calculate(target_date)
    disb_amount = Decimal(metrics.get('disbursementAmount') or '0')
    disb_count = int(metrics.get('disbursements') or 0)
    overdue_rate = _calc_overdue_rate(int(metrics.get('activeCases', 0)), max(int(metrics.get('applications', 0)), 1))
    summary = [
        ReportSummaryItem(label='放款金额', value=f"₵{disb_amount:,.0f}", delta=0.0, description='环比昨日'),
        ReportSummaryItem(label='放款笔数', value=str(disb_count), delta=0.0, description='环比昨日'),
        ReportSummaryItem(label='逾期率 (D1+)', value=f"{overdue_rate}%", delta=0.0, description='较昨日'),
        ReportSummaryItem(label='复借率', value='0%', delta=0.0, description='预研中'),
    ]
    channel_funnel_rows: List[ChannelFunnelRow] = []
    for row in metrics.get('channelFunnel', []):
        applies = int(row.get('applications') or 0)
        disburses = int(row.get('disbursements') or 0)
        conversion = round((disburses / applies) * 100, 1) if applies > 0 else 0.0
        channel_funnel_rows.append(
            ChannelFunnelRow(
                channel=row.get('channel') or 'unknown',
                installs=int(row.get('installs') or 0),
                registrations=int(row.get('registrations') or 0),
                applications=applies,
                disbursements=disburses,
                spend=str(row.get('spend') or '0.0000'),
                conversion=conversion,
            )
        )
    overdue_migration = [
        OverdueMigrationRow(stage='D0->D1', todayRate=overdue_rate, yesterdayRate=max(overdue_rate - 1, 0), change=-1.0),
        OverdueMigrationRow(stage='D1->D7', todayRate=max(overdue_rate - 5, 0), yesterdayRate=max(overdue_rate - 4, 0), change=-1.0),
    ]
    reborrow_rates = [
        ReborrowRateRow(segment='整体', rate=0.0, change=0.0, volume=0),
    ]
    return ReportCenterResponse(
        summary=summary,
        overdueMigration=overdue_migration,
        channelFunnel=channel_funnel_rows,
        reborrowRates=reborrow_rates,
        filters={
            'businessDate': target_date.isoformat(),
            'channel': channel,
            'product': product,
        },
        lastUpdated=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        notes=[],
    )


@router.post('/reports/center/export')
def export_report_center(businessDate: Optional[str] = Query(default=None)) -> dict:
    ts = int(datetime.utcnow().timestamp())
    day = _parse_date(businessDate) or date.today()
    return {'taskId': f'report-center-{day.isoformat()}-{ts}'}


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _calc_overdue_rate(active_cases: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((active_cases / denominator) * 100, 2)
