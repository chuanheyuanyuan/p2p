from __future__ import annotations

from typing import Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..config import Settings, get_settings
from ..data_access import (
    create_collection_action,
    get_collection_case,
    get_collection_stats,
    get_latest_device,
    list_collection_cases,
)
from ..schemas import (
    CollectionCaseDetail,
    CollectionCaseItem,
    CollectionStats,
    CollectionActionRequest,
    CollectionContact,
    CollectionFollowUp,
    CollectionPTPRecord,
    PaginatedCollectionCases,
)
from ..security import get_current_admin

router = APIRouter(
    prefix='/admin/v1/collections',
    tags=['Collections'],
    dependencies=[Depends(get_current_admin)],
)


@router.get('/cases', response_model=PaginatedCollectionCases)
def list_cases(
    bucket: Optional[str] = Query(default=None),
    assignee: Optional[str] = Query(default=None),
    caseId: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1, le=200),
    pageSize: int = Query(default=20, ge=1, le=200),
    settings: Settings = Depends(get_settings),
) -> PaginatedCollectionCases:
    rows, total = list_collection_cases(
        settings,
        bucket=bucket,
        assignee=assignee,
        case_id=caseId,
        status=status,
        page=page,
        page_size=pageSize,
    )
    items = [CollectionCaseItem(**row) for row in rows]
    return PaginatedCollectionCases(list=items, total=total)


@router.get('/cases/{case_id}', response_model=CollectionCaseDetail)
def case_detail(case_id: str, settings: Settings = Depends(get_settings)) -> CollectionCaseDetail:
    data = get_collection_case(settings, case_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='case not found')
    summary = CollectionCaseItem(**data['summary'])
    followups = [CollectionFollowUp(**item) for item in data['followUps']]
    ptp_records = [CollectionPTPRecord(**item) for item in data['ptpRecords']]
    device = get_latest_device(str(settings.user_db_path), summary.user)
    contact = CollectionContact(
        phone=device['device_id'] if device else None,
        whatsapp=None,
        address=None,
    )
    ptp_due_at = data['summary'].get('due')
    ptp_amount = data['summary'].get('amount')
    return CollectionCaseDetail(
        summary=summary,
        contact=contact,
        followUps=followups,
        ptpRecords=ptp_records,
        ptpDueAt=ptp_due_at,
        ptpAmount=float(ptp_amount) if ptp_amount is not None else None,
    )


@router.post('/cases/{case_id}/actions', response_model=CollectionCaseDetail)
def create_action(
    case_id: str,
    payload: CollectionActionRequest,
    settings: Settings = Depends(get_settings),
) -> CollectionCaseDetail:
    ptp_amount = Decimal(str(payload.ptpAmount)) if payload.ptpAmount is not None else None
    create_collection_action(
        settings,
        case_id,
        action_type=payload.action,
        actor='bff-admin',
        note=payload.note,
        result=payload.result,
        ptp_amount=ptp_amount,
        ptp_due_at=payload.ptpDueAt,
        status=payload.status,
    )
    data = get_collection_case(settings, case_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='case not found')
    summary = CollectionCaseItem(**data['summary'])
    followups = [CollectionFollowUp(**item) for item in data['followUps']]
    ptp_records = [CollectionPTPRecord(**item) for item in data['ptpRecords']]
    device = get_latest_device(str(settings.user_db_path), summary.user)
    contact = CollectionContact(
        phone=device['device_id'] if device else None,
        whatsapp=None,
        address=None,
    )
    return CollectionCaseDetail(
        summary=summary,
        contact=contact,
        followUps=followups,
        ptpRecords=ptp_records,
        ptpDueAt=data.get('ptpDueAt'),
        ptpAmount=data.get('ptpAmount'),
    )


@router.get('/stats', response_model=CollectionStats)
def collection_stats(settings: Settings = Depends(get_settings)) -> CollectionStats:
    stats = get_collection_stats(settings)
    return CollectionStats(**stats)
