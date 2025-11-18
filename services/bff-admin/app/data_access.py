from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from decimal import Decimal
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config import Settings


STATUS_LABELS = {
    'DRAFT': '草稿',
    'SUBMITTED': '审核中',
    'AUTO_CHECKING': '机审中',
    'AUTO_APPROVED': '通过',
    'AUTO_REJECTED': '拒绝',
    'REPAID': '已结清',
}


def _open_connection(path: Path) -> Optional[sqlite3.Connection]:
    if not path.exists():
        return None
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _parse_datetime(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).isoformat()
    except ValueError:
        return value


def _parse_decimal(value: Optional[str]) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


@lru_cache(maxsize=1)
def _load_products(products_path: str) -> Dict[str, str]:
    path = Path(products_path)
    if not path.exists():
        return {}
    try:
        items = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return {}
    return {item.get('productId'): item.get('name', item.get('productId')) for item in items}


def _loan_filters(
    status: Optional[str],
    user_id: Optional[str],
    keyword: Optional[str],
    product_id: Optional[str],
    start_date: Optional[str],
    end_date: Optional[str],
) -> Tuple[str, List[str]]:
    clauses: List[str] = []
    params: List[str] = []
    if status:
        clauses.append('la.status = ?')
        params.append(status)
    if user_id:
        clauses.append('la.user_id = ?')
        params.append(user_id)
    if keyword:
        clauses.append('(la.loan_id LIKE ? OR la.user_id LIKE ?)')
        like = f'%{keyword}%'
        params.extend([like, like])
    if product_id:
        clauses.append('la.product_id = ?')
        params.append(product_id)
    if start_date:
        clauses.append('la.created_at >= ?')
        params.append(start_date)
    if end_date:
        clauses.append('la.created_at <= ?')
        params.append(end_date)
    where_clause = ' WHERE ' + ' AND '.join(clauses) if clauses else ''
    return where_clause, params


def list_applications(
    settings: Settings,
    *,
    status: Optional[str] = None,
    user_id: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    *,
    product_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = None,
) -> Tuple[List[dict], int]:
    conn = _open_connection(settings.loan_db_path)
    if conn is None:
        return [], 0
    try:
        where_clause, params = _loan_filters(status, user_id, keyword, product_id, start_date, end_date)
        total = conn.execute(
            f'SELECT COUNT(*) FROM loan_applications la{where_clause}',
            params,
        ).fetchone()[0]
        query = (
            'SELECT la.*, rs.original_amount, rs.outstanding_amount, rs.paid_amount, rs.last_paid_at '
            'FROM loan_applications la '
            'LEFT JOIN repayment_schedules rs ON la.loan_id = rs.loan_id'
            f'{where_clause} '
            'ORDER BY la.created_at DESC '
        )
        if limit is not None:
            query += 'LIMIT ?'
            rows = conn.execute(query, (*params, limit)).fetchall()
        else:
            offset = (page - 1) * page_size
            query += 'LIMIT ? OFFSET ?'
            rows = conn.execute(query, (*params, page_size, offset)).fetchall()
    except sqlite3.Error:
        return [], 0
    finally:
        conn.close()

    products = _load_products(str(settings.loan_db_path.parent / 'products.json'))
    results: List[dict] = []
    for row in rows:
        product_id = row['product_id']
        record = {
            'id': row['loan_id'],
            'userId': row['user_id'],
            'productId': product_id,
            'product': products.get(product_id, product_id),
            'amount': float(row['requested_amount']),
            'termDays': row['term_days'],
            'status': row['status'],
            'statusCode': row['decision_reason'],
            'decision': row['decision_reason'],
            'score': row['score'],
            'createdAt': row['created_at'],
            'updatedAt': row['updated_at'],
            'originalAmount': _parse_decimal(row['original_amount']),
            'outstandingAmount': _parse_decimal(row['outstanding_amount']),
            'lastPaidAt': _parse_datetime(row['last_paid_at']),
        }
        results.append(record)
    return results, int(total or 0)


def get_application(settings: Settings, loan_id: str) -> Optional[dict]:
    conn = _open_connection(settings.loan_db_path)
    if conn is None:
        return None
    try:
        row = conn.execute(
            'SELECT la.*, rs.original_amount, rs.outstanding_amount, rs.paid_amount, rs.last_paid_at '
            'FROM loan_applications la '
            'LEFT JOIN repayment_schedules rs ON la.loan_id = rs.loan_id '
            'WHERE la.loan_id = ?',
            (loan_id,),
        ).fetchone()
    except sqlite3.Error:
        row = None
    finally:
        conn.close()
    if not row:
        return None
    products = _load_products(str(settings.loan_db_path.parent / 'products.json'))
    product_id = row['product_id']
    return {
        'id': row['loan_id'],
        'userId': row['user_id'],
        'productId': product_id,
        'product': products.get(product_id, product_id),
        'amount': float(row['requested_amount']),
        'termDays': row['term_days'],
        'status': row['status'],
        'statusCode': row['decision_reason'],
        'decision': row['decision_reason'],
        'score': row['score'],
        'createdAt': row['created_at'],
        'updatedAt': row['updated_at'],
        'originalAmount': _parse_decimal(row['original_amount']),
        'outstandingAmount': _parse_decimal(row['outstanding_amount']),
        'lastPaidAt': _parse_datetime(row['last_paid_at']),
    }


@lru_cache(maxsize=512)
def get_latest_device(db_path: str, user_id: str) -> Optional[dict]:
    path = Path(db_path)
    if not path.exists():
        return None
    conn = _open_connection(path)
    if conn is None:
        return None
    try:
        row = conn.execute(
            'SELECT * FROM user_devices WHERE user_id = ? ORDER BY last_active_at DESC LIMIT 1',
            (user_id,),
        ).fetchone()
    except sqlite3.Error:
        row = None
    finally:
        conn.close()
    return dict(row) if row else None


@lru_cache(maxsize=512)
def get_user_kyc(db_path: str, user_id: str) -> Optional[dict]:
    path = Path(db_path)
    if not path.exists():
        return None
    conn = _open_connection(path)
    if conn is None:
        return None
    try:
        row = conn.execute('SELECT * FROM user_kyc WHERE user_id = ?', (user_id,)).fetchone()
    except sqlite3.Error:
        row = None
    finally:
        conn.close()
    return dict(row) if row else None


def count_loans_for_user(settings: Settings, user_id: str) -> int:
    conn = _open_connection(settings.loan_db_path)
    if conn is None:
        return 0
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM loan_applications WHERE user_id = ? AND status != 'DRAFT'",
            (user_id,),
        ).fetchone()
    except sqlite3.Error:
        row = None
    finally:
        conn.close()
    if not row:
        return 0
    return int(row[0] or 0)


def list_collection_cases(
    settings: Settings,
    *,
    bucket: Optional[str] = None,
    assignee: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[dict], int]:
    conn = _open_connection(settings.collection_db_path)
    if conn is None:
        return [], 0
    clauses: List[str] = []
    params: List[str] = []
    if bucket:
        clauses.append('bucket = ?')
        params.append(bucket)
    if assignee:
        clauses.append('assigned_to = ?')
        params.append(assignee)
    where_clause = ' WHERE ' + ' AND '.join(clauses) if clauses else ''
    try:
        total = conn.execute(f'SELECT COUNT(*) FROM collection_cases{where_clause}', params).fetchone()[0]
        offset = (page - 1) * page_size
        rows = conn.execute(
            f'SELECT * FROM collection_cases{where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (*params, page_size, offset),
        ).fetchall()
    except sqlite3.Error:
        conn.close()
        return [], 0
    finally:
        conn.close()

    cases: List[dict] = []
    for row in rows:
        principal = _parse_decimal(row['principal_due']) or Decimal('0')
        overdue_days = _bucket_overdue_days(row['bucket'])
        ptp_status = None
        if row['ptp_due_at']:
            ptp_status = f"PTP {row['ptp_due_at'].split('T')[0]}"
        cases.append(
            {
                'caseId': row['case_id'],
                'user': row['user_id'],
                'bucket': row['bucket'],
                'amount': float(principal),
                'principalDue': float(principal),
                'overdueDays': overdue_days,
                'ptpStatus': ptp_status,
                'assignee': row['assigned_to'],
                'channel': 'loan-app',
                'due': row['ptp_due_at'],
                'status': row['status'],
            }
        )
    return cases, int(total or 0)


def _bucket_overdue_days(bucket: Optional[str]) -> int:
    if not bucket:
        return 0
    digits = ''.join(ch for ch in bucket if ch.isdigit())
    return int(digits or 0)


def get_collection_case(settings: Settings, case_id: str) -> Optional[dict]:
    conn = _open_connection(settings.collection_db_path)
    if conn is None:
        return None
    try:
        row = conn.execute('SELECT * FROM collection_cases WHERE case_id = ?', (case_id,)).fetchone()
        if not row:
            return None
        actions = conn.execute(
            'SELECT * FROM collection_actions WHERE case_id = ? ORDER BY created_at DESC',
            (case_id,),
        ).fetchall()
    except sqlite3.Error:
        return None
    finally:
        conn.close()

    principal = _parse_decimal(row['principal_due']) or Decimal('0')
    summary = {
        'caseId': row['case_id'],
        'user': row['user_id'],
        'bucket': row['bucket'],
        'amount': float(principal),
        'principalDue': float(principal),
        'overdueDays': _bucket_overdue_days(row['bucket']),
        'ptpStatus': row['last_action'],
        'assignee': row['assigned_to'],
        'channel': 'loan-app',
        'due': row['ptp_due_at'],
        'status': row['status'],
    }
    followups: List[dict] = []
    ptp_records: List[dict] = []
    for act in actions:
        ts = _parse_datetime(act['created_at']) or act['created_at']
        followups.append(
            {
                'ts': ts,
                'actor': act['actor'],
                'action': act['action_type'],
                'result': act['result'],
            }
        )
        if act['ptp_amount']:
            status_label = '有效'
            if row['ptp_due_at'] and datetime.fromisoformat(row['ptp_due_at']) < datetime.utcnow():
                status_label = '失效'
            ptp_records.append(
                {
                    'ts': ts,
                    'amount': float(_parse_decimal(act['ptp_amount']) or Decimal('0')),
                    'promiseDate': act['ptp_due_at'],
                    'status': status_label,
                    'note': act['note'],
                }
            )
    return {
        'summary': summary,
        'followUps': followups,
        'ptpRecords': ptp_records,
    }


def get_user_profile(settings: Settings, user_id: str) -> dict:
    device = get_latest_device(str(settings.user_db_path), user_id)
    kyc = get_user_kyc(str(settings.user_db_path), user_id)
    loans, _ = list_applications(
        settings,
        user_id=user_id,
        page=1,
        page_size=settings.max_application_rows,
        limit=settings.max_application_rows,
    )
    outstanding_total = Decimal('0')
    active_loans = 0
    for loan in loans:
        outstanding_total += loan.get('outstandingAmount') or Decimal('0')
        if loan['status'] not in ('AUTO_REJECTED', 'REPAID', 'DRAFT'):
            active_loans += 1
    last_loan = loans[0] if loans else None
    loan_summary = {
        'totalLoans': len(loans),
        'activeLoans': active_loans,
        'outstandingAmount': outstanding_total,
        'lastLoanId': last_loan['id'] if last_loan else None,
        'lastStatus': STATUS_LABELS.get(last_loan['status'], last_loan['status']) if last_loan else None,
        'lastSubmittedAt': last_loan['createdAt'] if last_loan else None,
        'repeat': len(loans) > 1,
    }
    device_info = None
    if device:
        device_info = {
            'deviceId': device.get('device_id'),
            'platform': device.get('platform'),
            'appVersion': device.get('app_version'),
            'lastActiveAt': device.get('last_active_at'),
            'privacyConsent': bool(device.get('privacy_consent')),
            'locationConsent': bool(device.get('location_consent')),
        }
    kyc_info = None
    if kyc:
        kyc_info = {
            'status': kyc.get('kyc_status', 'UNKNOWN'),
            'docType': kyc.get('doc_type'),
            'docNumber': kyc.get('doc_number'),
            'reviewer': kyc.get('reviewer'),
            'reviewedAt': kyc.get('reviewed_at'),
        }
    collection_summary = _get_collection_summary(settings, user_id)

    tags: List[str] = []
    risk_flags: List[str] = []
    if kyc and kyc.get('kyc_status') != 'APPROVED':
        risk_flags.append('KYC_PENDING')
    if outstanding_total > Decimal('0'):
        risk_flags.append('OUTSTANDING_BALANCE')
    if device_info and device_info.get('privacyConsent'):
        tags.append('已授权')
    if loan_summary['repeat']:
        tags.append('复借用户')
    return {
        'userId': user_id,
        'name': f'Borrower {user_id}',
        'gender': None,
        'phone': None,
        'email': None,
        'level': loan_summary['repeat'] and 'Level2' or 'Level1',
        'kycStatus': kyc.get('kyc_status') if kyc else 'UNKNOWN',
        'registerDate': device['created_at'] if device else None,
        'lastLogin': device['last_active_at'] if device else None,
        'tags': tags,
        'riskFlags': risk_flags,
        'address': None,
        'gps': None,
        'blacklisted': bool(kyc and kyc.get('kyc_status') == 'REJECTED'),
        'loanSummary': loan_summary,
        'device': device_info,
        'kyc': kyc_info,
        'collectionSummary': collection_summary,
    }


def _get_collection_summary(settings: Settings, user_id: str) -> dict:
    conn = _open_connection(settings.collection_db_path)
    if conn is None:
        return {'openCases': 0, 'lastBucket': None, 'lastStatus': None, 'lastActionAt': None}
    try:
        rows = conn.execute(
            'SELECT bucket, status, updated_at, created_at FROM collection_cases WHERE user_id = ? ORDER BY updated_at DESC',
            (user_id,),
        ).fetchall()
    except sqlite3.Error:
        conn.close()
        return {'openCases': 0, 'lastBucket': None, 'lastStatus': None, 'lastActionAt': None}
    finally:
        conn.close()
    if not rows:
        return {'openCases': 0, 'lastBucket': None, 'lastStatus': None, 'lastActionAt': None}
    open_cases = sum(1 for row in rows if row['status'] not in ('PAID', 'CLOSED', 'RESOLVED'))
    latest = rows[0]
    return {
        'openCases': open_cases,
        'lastBucket': latest['bucket'],
        'lastStatus': latest['status'],
        'lastActionAt': latest['updated_at'] or latest['created_at'],
    }
