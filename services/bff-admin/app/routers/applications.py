from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..config import Settings, get_settings
from ..data_access import (
    count_loans_for_user,
    get_application,
    get_latest_device,
    get_user_kyc,
    list_applications,
)
from ..schemas import (
    ApplicationBasicInfo,
    ApplicationCustomerProfile,
    ApplicationDetail,
    ApplicationDocument,
    ApplicationHistoryEntry,
    ApplicationRecord,
    ApprovalNode,
    ApprovalSummary,
    PaginatedApplications,
)
from ..security import get_current_admin

router = APIRouter(prefix='/admin/v1', tags=['Applications'], dependencies=[Depends(get_current_admin)])


@router.get('/applications', response_model=PaginatedApplications)
def list_application_view(
    status: Optional[str] = Query(default=None),
    userId: Optional[str] = Query(default=None),
    loanId: Optional[str] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1, le=200),
    pageSize: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> PaginatedApplications:
    filters_keyword = loanId or keyword
    rows, total = list_applications(
        settings,
        status=status,
        user_id=userId,
        keyword=filters_keyword,
        page=page,
        page_size=pageSize,
    )
    records: List[ApplicationRecord] = [_to_application_record(row, settings) for row in rows]
    return PaginatedApplications(list=records, total=total)


@router.get('/applications/{loan_id}', response_model=ApplicationDetail)
def get_application_detail(loan_id: str, settings: Settings = Depends(get_settings)) -> ApplicationDetail:
    data = get_application(settings, loan_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='loan not found')
    record = _to_application_record(data, settings)
    device = get_latest_device(str(settings.user_db_path), record.userId)
    kyc = get_user_kyc(str(settings.user_db_path), record.userId)
    basic = ApplicationBasicInfo(
        applyTime=record.submittedAt,
        productVersion='v1',
        deviceBrand=device['platform'] if device else 'unknown',
        deviceModel=device['device_id'] if device else 'unknown',
        appVersion=record.appVersion,
        platform=device['platform'] if device else 'android',
        source='app',
    )
    customer = ApplicationCustomerProfile(
        sim=device['device_id'] if device else 'unknown',
        email=kyc.get('doc_number') if kyc else None,
        gender=None,
        age=None,
        idType=kyc.get('doc_type') if kyc else None,
        idNumber=kyc.get('doc_number') if kyc else None,
        education=None,
        maritalStatus=None,
        address=None,
        gps=None,
    )
    history = _build_history(record)
    approval = _build_approval(record)
    approval_summary = ApprovalSummary(
        autoDecision=record.autoDecision,
        manualDecision=record.status,
        riskScore=record.riskScore,
        reasons=record.tags or ['系统自动决策'],
    )
    documents = _build_documents(record)
    return ApplicationDetail(
        application=record,
        basic=basic,
        customer=customer,
        approval=approval,
        approvalSummary=approval_summary,
        history=history,
        documents=documents,
    )


@router.post('/applications/export')
def export_applications() -> dict:
    task_id = f'app-export-{int(datetime.utcnow().timestamp())}'
    return {'taskId': task_id}


def _to_application_record(row: dict, settings: Settings) -> ApplicationRecord:
    created = _format_time(row['createdAt'])
    device = get_latest_device(str(settings.user_db_path), row['userId'])
    repeat = count_loans_for_user(settings, row['userId']) > 1
    status_label = STATUS_LABELS.get(row['status'], row['status'])
    last_paid = row.get('lastPaidAt')
    return ApplicationRecord(
        id=row['id'],
        userId=row['userId'],
        product=row['product'],
        productId=row['productId'],
        name=f"Borrower {row['userId']}",
        phone=None,
        channel='app',
        level='Level1',
        amount=row['amount'],
        term=f"{row.get('termDays', 0)}D",
        reviewer='系统',
        status=status_label,
        statusCode=row.get('statusCode'),
        submittedAt=created,
        appVersion=device['app_version'] if device else None,
        tags=['自动导入'] if row.get('decision') else [],
        repeat=repeat,
        riskScore=row.get('score'),
        autoDecision=row.get('decision'),
        outstandingAmount=row.get('outstandingAmount'),
        originalAmount=row.get('originalAmount'),
        lastPaidAt=last_paid,
    )


def _format_time(value: Optional[str]) -> str:
    if not value:
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    try:
        return datetime.fromisoformat(value).strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return value


def _build_history(record: ApplicationRecord) -> List[ApplicationHistoryEntry]:
    return [
        ApplicationHistoryEntry(ts=record.submittedAt, event='提交申请', actor=record.name),
        ApplicationHistoryEntry(ts=record.submittedAt, event='机审完成', actor='风险系统'),
        ApplicationHistoryEntry(ts=record.submittedAt, event='审批完成', actor='审批员'),
    ]


def _build_approval(record: ApplicationRecord) -> List[ApprovalNode]:
    now = record.submittedAt
    return [
        ApprovalNode(node='机审', result=record.autoDecision or 'AUTO', operator='系统', time=now),
        ApprovalNode(node='人工审批', result=record.status, operator='审批员', time=now),
    ]


def _build_documents(record: ApplicationRecord) -> List[ApplicationDocument]:
    base_url = f'https://static.local/contracts/{record.id}'
    return [
        ApplicationDocument(type='OCR', name='身份证', url=f'{base_url}/ocr.pdf', updatedAt=record.submittedAt),
        ApplicationDocument(type='合同', name='借款合同', url=f'{base_url}/contract.pdf', updatedAt=record.submittedAt),
    ]


STATUS_LABELS = {
    'DRAFT': '草稿',
    'SUBMITTED': '审核中',
    'AUTO_CHECKING': '机审中',
    'AUTO_APPROVED': '通过',
    'AUTO_REJECTED': '拒绝',
}
