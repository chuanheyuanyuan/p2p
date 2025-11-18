from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends
from httpx import AsyncClient, HTTPStatusError, RequestError

from ..config import Settings, get_settings
from ..dependencies import get_http_client
from ..http_utils import build_service_url, translate_http_error
from ..schemas import DashboardMetrics, DashboardResponse, LoanSummary, ProductSummary
from ..security import BorrowerContext, get_borrower_context

router = APIRouter()


@router.get('/mobile/v1/dashboard', response_model=DashboardResponse)
async def get_dashboard(
    borrower: BorrowerContext = Depends(get_borrower_context),
    http_client: AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings)
) -> DashboardResponse:
    loans = await _fetch_loans(http_client, settings, borrower.userId)
    metrics = _build_metrics(loans)
    products = await _fetch_recommendations(http_client, settings)
    return DashboardResponse(userId=borrower.userId, metrics=metrics, loans=loans, recommendations=products)


async def _fetch_loans(http_client: AsyncClient, settings: Settings, user_id: str) -> List[LoanSummary]:
    url = build_service_url(settings.loan_base_url, f'/users/{user_id}/loans')
    try:
        response = await http_client.get(url, params={'limit': settings.loan_list_limit})
        response.raise_for_status()
    except (HTTPStatusError, RequestError) as exc:  # pragma: no cover
        translate_http_error(exc)
    payload = response.json()
    raw_items = payload.get('items', []) if isinstance(payload, dict) else []
    return [_normalize_loan(item) for item in raw_items]


async def _fetch_recommendations(http_client: AsyncClient, settings: Settings) -> List[ProductSummary]:
    url = build_service_url(settings.loan_base_url, '/loan/products')
    try:
        response = await http_client.get(url)
        response.raise_for_status()
    except (HTTPStatusError, RequestError) as exc:  # pragma: no cover
        translate_http_error(exc)
    payload = response.json()
    raw_items = payload.get('items', []) if isinstance(payload, dict) else []
    return [
        ProductSummary(
            productId=item.get('productId', ''),
            name=item.get('name', ''),
            currency=item.get('currency', 'GHS'),
            amountMin=item.get('amountMin', 0.0),
            amountMax=item.get('amountMax', 0.0),
            defaultTerm=item.get('defaultTerm', 0),
            termOptions=item.get('termOptions', []),
        )
        for item in raw_items
        if item.get('enabled', True)
    ][: settings.recommendation_limit]


def _build_metrics(loans: List[LoanSummary]) -> DashboardMetrics:
    total_outstanding = sum(loan.outstandingAmount for loan in loans)
    active_loans = [loan for loan in loans if loan.status.upper() not in {'REPAID', 'CLOSED'}]
    last_activity = max((loan.updatedAt for loan in loans), default=None)
    return DashboardMetrics(totalOutstanding=total_outstanding, activeLoans=len(active_loans), lastActivityAt=last_activity)


def _normalize_loan(item: dict) -> LoanSummary:
    return LoanSummary(
        loanId=item.get('loanId', ''),
        productId=item.get('productId', ''),
        amount=_to_decimal(item.get('amount')),
        termDays=item.get('termDays', 0),
        status=item.get('status', 'UNKNOWN'),
        outstandingAmount=_to_decimal(item.get('outstandingAmount')),
        originalAmount=_to_decimal(item.get('originalAmount')),
        lastPaidAt=item.get('lastPaidAt'),
        createdAt=item.get('createdAt'),
        updatedAt=item.get('updatedAt'),
    )


def _to_decimal(value: object) -> Decimal:
    if value is None:
        return Decimal('0')
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))
