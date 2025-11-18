from typing import List, Optional

from fastapi import APIRouter, Depends, Header, status
from httpx import AsyncClient, HTTPStatusError, RequestError

from ..config import Settings, get_settings
from ..dependencies import get_http_client
from ..http_utils import build_service_url, translate_http_error
from ..schemas import LoanCreateRequest, LoanCreateResponse, LoanListResponse, LoanSummary
from ..security import BorrowerContext, get_borrower_context
from .dashboard import _normalize_loan  # reuse helper

router = APIRouter()


@router.get('/mobile/v1/loans', response_model=LoanListResponse)
async def list_loans(
    borrower: BorrowerContext = Depends(get_borrower_context),
    http_client: AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings)
) -> LoanListResponse:
    loans = await _fetch_loans(http_client, settings, borrower.userId)
    return LoanListResponse(items=loans, total=len(loans))


@router.post('/mobile/v1/loans', response_model=LoanCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    payload: LoanCreateRequest,
    borrower: BorrowerContext = Depends(get_borrower_context),
    http_client: AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    x_idempotency_key: Optional[str] = Header(default=None, alias='X-Idempotency-Key')
) -> LoanCreateResponse:
    url = build_service_url(settings.loan_base_url, '/loans')
    body = payload.model_dump()
    body['userId'] = borrower.userId
    headers = {'X-Idempotency-Key': x_idempotency_key} if x_idempotency_key else None
    try:
        response = await http_client.post(url, json=body, headers=headers)
        response.raise_for_status()
    except (HTTPStatusError, RequestError) as exc:  # pragma: no cover - translation tested elsewhere
        translate_http_error(exc)
    data = response.json()
    return LoanCreateResponse(**data)


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
