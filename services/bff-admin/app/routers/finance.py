from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from ..config import Settings, get_settings
from ..data_access import list_disbursements, list_reconciliations, list_repayments
from ..schemas import PaginatedDisbursements, PaginatedReconciliations, PaginatedRepayments
from ..security import get_current_admin

router = APIRouter(
    prefix='/admin/v1/finance',
    tags=['Finance'],
    dependencies=[Depends(get_current_admin)],
)


@router.get('/disbursements', response_model=PaginatedDisbursements)
def disbursements(
    status: Optional[str] = Query(default=None),
    channel: Optional[str] = Query(default=None),
    loanId: Optional[str] = Query(default=None),
    startDate: Optional[str] = Query(default=None),
    endDate: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1, le=200),
    pageSize: int = Query(default=20, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> PaginatedDisbursements:
    rows, total = list_disbursements(
        settings,
        status=status,
        channel=channel,
        loan_id=loanId,
        start_date=startDate,
        end_date=endDate,
        page=page,
        page_size=pageSize,
    )
    return PaginatedDisbursements(list=rows, total=total)


@router.get('/repayments', response_model=PaginatedRepayments)
def repayments(
    status: Optional[str] = Query(default=None),
    channel: Optional[str] = Query(default=None),
    loanId: Optional[str] = Query(default=None),
    startDate: Optional[str] = Query(default=None),
    endDate: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1, le=200),
    pageSize: int = Query(default=20, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> PaginatedRepayments:
    rows, total = list_repayments(
        settings,
        status=status,
        channel=channel,
        loan_id=loanId,
        start_date=startDate,
        end_date=endDate,
        page=page,
        page_size=pageSize,
    )
    return PaginatedRepayments(list=rows, total=total)


@router.get('/reconciliations', response_model=PaginatedReconciliations)
def reconciliations(
    refType: Optional[str] = Query(default=None),
    refId: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1, le=200),
    pageSize: int = Query(default=20, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> PaginatedReconciliations:
    rows, total = list_reconciliations(
        settings,
        ref_type=refType,
        ref_id=refId,
        page=page,
        page_size=pageSize,
    )
    return PaginatedReconciliations(list=rows, total=total)
