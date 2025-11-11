from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from .config import get_settings


def post_repayment_to_loan_svc(
    loan_id: str,
    amount: Decimal,
    currency: str,
    paid_at: Optional[datetime]
) -> Dict[str, Any]:
    settings = get_settings()
    base_url = settings.loan_svc_base_url.rstrip('/')
    url = f"{base_url}/loans/{loan_id}/repayments"
    payload: Dict[str, Any] = {
        'amount': str(amount),
        'currency': currency,
    }
    if paid_at:
        payload['paidAt'] = paid_at.isoformat()
    try:
        response = httpx.post(url, json=payload, timeout=settings.loan_svc_timeout)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'loan-svc unavailable: {exc}'
        ) from exc
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
