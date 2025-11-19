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
    phone: Optional[str] = Query(default=None),
    channel: Optional[str] = Query(default=None),
    product: Optional[str] = Query(default=None),
    level: Optional[str] = Query(default=None),
    appVersion: Optional[str] = Query(default=None),
    reviewer: Optional[str] = Query(default=None),
    repeat: Optional[str] = Query(default=None),
    startDate: Optional[str] = Query(default=None),
    endDate: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1, le=200),
    pageSize: int = Query(default=20, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> PaginatedApplications:
    filters_keyword = loanId or keyword
    start_ts = _normalize_date(startDate, end=False)
    end_ts = _normalize_date(endDate, end=True)
    rows, _ = list_applications(
        settings,
        status=status,
        user_id=userId,
        keyword=filters_keyword,
        page=1,
        page_size=settings.max_application_rows,
        start_date=start_ts,
        end_date=end_ts,
        limit=settings.max_application_rows,
        phone=phone,
        channel=channel,
        repeat=repeat,
    )
    records: List[ApplicationRecord] = [_to_application_record(row, settings) for row in rows]
    filtered_records = _apply_application_filters(
        records,
        phone=phone,
        channel=channel,
        product=product,
        level=level,
        app_version=appVersion,
        reviewer=reviewer,
        repeat=repeat,
        loan_id=loanId,
    )
    total = len(filtered_records)
    start = (page - 1) * pageSize
    end_idx = start + pageSize
    page_items = filtered_records[start:end_idx]
    return PaginatedApplications(list=page_items, total=total)


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
    documents = _build_documents(record, data.get('documents'))
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
    loan_count = count_loans_for_user(settings, row['userId'])
    profile_repeat = row.get('isRepeat')
    repeat = bool(profile_repeat) if profile_repeat is not None else loan_count > 1
    status_label = STATUS_LABELS.get(row['status'], row['status'])
    last_paid = row.get('lastPaidAt')
    phone = row.get('phone') or _fake_phone(row['userId'])
    channel = row.get('channel') or _derive_channel(row.get('productId'), row['userId'])
    reviewer = row.get('reviewer') or _derive_reviewer(repeat)
    tags = row.get('tags') or (['自动导入'] if row.get('decision') else [])
    return ApplicationRecord(
        id=row['id'],
        userId=row['userId'],
        product=row['product'],
        productId=row['productId'],
        name=f"Borrower {row['userId']}",
        phone=phone,
        channel=channel,
        level=_derive_level(loan_count),
        amount=row['amount'],
        term=f"{row.get('termDays', 0)}D",
        reviewer=reviewer,
        status=status_label,
        statusCode=row.get('statusCode'),
        submittedAt=created,
        appVersion=device['app_version'] if device else None,
        tags=tags,
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


def _build_documents(record: ApplicationRecord, attachments: Optional[List[dict]]) -> List[ApplicationDocument]:
    documents: List[ApplicationDocument] = []
    if attachments:
        for item in attachments:
            documents.append(
                ApplicationDocument(
                    type=item.get('type', '附件'),
                    name=item.get('name', item.get('type', '附件')),
                    url=item.get('url', ''),
                    updatedAt=item.get('updatedAt') or record.submittedAt,
                )
            )
        return documents
    base_url = f'https://static.local/contracts/{record.id}'
    return [
        ApplicationDocument(type='OCR', name='身份证', url=f'{base_url}/ocr.pdf', updatedAt=record.submittedAt),
        ApplicationDocument(type='合同', name='借款合同', url=f'{base_url}/contract.pdf', updatedAt=record.submittedAt),
    ]


def _normalize_date(value: Optional[str], end: bool) -> Optional[str]:
    if not value:
        return None
    if 'T' in value:
        return value
    suffix = 'T23:59:59' if end else 'T00:00:00'
    return f'{value}{suffix}'


def _apply_application_filters(
    records: List[ApplicationRecord],
    *,
    phone: Optional[str],
    channel: Optional[str],
    product: Optional[str],
    level: Optional[str],
    app_version: Optional[str],
    reviewer: Optional[str],
    repeat: Optional[str],
    loan_id: Optional[str],
) -> List[ApplicationRecord]:
    def matches(record: ApplicationRecord) -> bool:
        if phone and phone.lower() not in (record.phone or '').lower():
            return False
        if channel and record.channel != channel:
            return False
        if product and record.product != product and record.productId != product:
            return False
        if level and record.level != level:
            return False
        if app_version and record.appVersion != app_version:
            return False
        if reviewer and record.reviewer != reviewer:
            return False
        if repeat == 'yes' and not record.repeat:
            return False
        if repeat == 'no' and record.repeat:
            return False
        if loan_id and record.id != loan_id:
            return False
        return True

    return [rec for rec in records if matches(rec)]


def _fake_phone(user_id: str) -> str:
    digits = ''.join(ch for ch in user_id if ch.isdigit())
    seed = digits or str(abs(hash(user_id)))
    suffix = seed.zfill(4)[-4:]
    return f'+233-55{suffix}'


CHANNEL_POOL = ['Google Ads', 'Facebook Ads', 'Affiliate', 'App Organic']


def _derive_channel(product_id: Optional[str], user_id: str) -> str:
    key = f'{product_id or ""}{user_id}'
    return CHANNEL_POOL[abs(hash(key)) % len(CHANNEL_POOL)]


def _derive_level(loan_count: int) -> str:
    if loan_count >= 5:
        return 'Level5'
    if loan_count == 4:
        return 'Level4'
    if loan_count == 3:
        return 'Level3'
    if loan_count == 2:
        return 'Level2'
    return 'Level1'


def _derive_reviewer(is_repeat: bool) -> str:
    return '资深审批员' if is_repeat else '系统'


STATUS_LABELS = {
    'DRAFT': '草稿',
    'SUBMITTED': '审核中',
    'AUTO_CHECKING': '机审中',
    'AUTO_APPROVED': '通过',
    'AUTO_REJECTED': '拒绝',
}
