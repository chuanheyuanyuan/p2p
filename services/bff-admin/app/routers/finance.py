from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..config import Settings, get_settings
from ..data_access import list_disbursements, list_repayments, list_reconciliations
from ..schemas import (
    PaginatedDisbursements,
    PaginatedReconciliations,
    PaginatedRepayments,
)
from ..security import get_current_admin

router = APIRouter(prefix='/admin/v1/finance', tags=['Finance'], dependencies=[Depends(get_current_admin)])


@router.get('/disbursements', response_model=PaginatedDisbursements)
def list_disbursement_view(
    status: str | None = Query(default=None),
    channel: str | None = Query(default=None),
    loanId: str | None = Query(default=None),
    startDate: str | None = Query(default=None),
    endDate: str | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=200),
    pageSize: int = Query(default=20, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> PaginatedDisbursements:
    records, total = list_disbursements(
        settings,
        status=status,
        channel=channel,
        loan_id=loanId,
        start_date=startDate,
        end_date=endDate,
        page=page,
        page_size=pageSize,
    )
    return PaginatedDisbursements(list=records, total=total)


@router.get('/repayments', response_model=PaginatedRepayments)
def list_repayment_view(
    status: str | None = Query(default=None),
    channel: str | None = Query(default=None),
    loanId: str | None = Query(default=None),
    startDate: str | None = Query(default=None),
    endDate: str | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=200),
    pageSize: int = Query(default=20, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> PaginatedRepayments:
    records, total = list_repayments(
        settings,
        status=status,
        channel=channel,
        loan_id=loanId,
        start_date=startDate,
        end_date=endDate,
        page=page,
        page_size=pageSize,
    )
    return PaginatedRepayments(list=records, total=total)


@router.get('/reconciliations', response_model=PaginatedReconciliations)
def list_reconciliations_view(
    refType: str | None = Query(default=None),
    refId: str | None = Query(default=None),
    page: int = Query(default=1, ge=1, le=200),
    pageSize: int = Query(default=20, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> PaginatedReconciliations:
    records, total = list_reconciliations(
        settings,
        ref_type=refType,
        ref_id=refId,
        page=page,
        page_size=pageSize,
    )
    return PaginatedReconciliations(list=records, total=total)
