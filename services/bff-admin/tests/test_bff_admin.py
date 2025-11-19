from importlib import reload
from pathlib import Path
import sqlite3
import sys
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    loan_db = tmp_path / 'loan.db'
    user_db = tmp_path / 'user.db'
    collection_db = tmp_path / 'collection.db'
    payment_db = tmp_path / 'payment.db'
    ledger_db = tmp_path / 'ledger.db'
    admin_db = tmp_path / 'admin.db'
    products_path = tmp_path / 'products.json'

    _seed_loan_db(loan_db)
    _seed_user_db(user_db)
    _seed_collection_db(collection_db)
    _seed_payment_db(payment_db)
    _seed_ledger_db(ledger_db)
    products_path.write_text(
        '[{"productId":"P_BASIC","name":"InsCash Basic"},{"productId":"P_MAX","name":"InsCash Max"}]',
        encoding='utf-8',
    )

    monkeypatch.setenv('BFF_ADMIN_LOAN_DB_PATH', str(loan_db))
    monkeypatch.setenv('BFF_ADMIN_USER_DB_PATH', str(user_db))
    monkeypatch.setenv('BFF_ADMIN_COLLECTION_DB_PATH', str(collection_db))
    monkeypatch.setenv('BFF_ADMIN_PAYMENT_DB_PATH', str(payment_db))
    monkeypatch.setenv('BFF_ADMIN_LEDGER_DB_PATH', str(ledger_db))
    monkeypatch.setenv('BFF_ADMIN_ADMIN_DB_PATH', str(admin_db))

    import app.config as config

    config.get_settings.cache_clear()
    reload(config)
    import app.main as main

    reload(main)
    with TestClient(main.app) as test_client:
        yield test_client


def _seed_loan_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        '''
        CREATE TABLE loan_applications (
            loan_id TEXT PRIMARY KEY,
            user_id TEXT,
            product_id TEXT,
            requested_amount REAL,
            term_days INTEGER,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            decision_reason TEXT,
            score INTEGER
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE repayment_schedules (
            loan_id TEXT PRIMARY KEY,
            currency TEXT,
            original_amount TEXT,
            outstanding_amount TEXT,
            paid_amount TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            last_paid_at TEXT
        )
        '''
    )
    now = datetime.utcnow().isoformat()
    earlier = (datetime.utcnow() - timedelta(days=7)).isoformat()
    rows = [
        ('LN123', 'U1', 'P_BASIC', 500, 7, 'SUBMITTED', now, now, 'AUTO_PASS', 720),
        ('LN124', 'U1', 'P_BASIC', 800, 14, 'AUTO_APPROVED', earlier, earlier, 'AUTO_PASS', 710),
        ('LN777', 'U3', 'P_MAX', 1000, 30, 'AUTO_REJECTED', now, now, 'AUTO_REVIEW', 610),
    ]
    conn.executemany('INSERT INTO loan_applications VALUES (?,?,?,?,?,?,?,?,?,?)', rows)
    schedules = [
        ('LN123', 'GHS', '500', '250', '250', 'ACTIVE', now, now, now),
        ('LN124', 'GHS', '800', '0', '800', 'REPAID', earlier, now, earlier),
        ('LN777', 'GHS', '1000', '1000', '0', 'ACTIVE', now, now, None),
    ]
    conn.executemany(
        'INSERT INTO repayment_schedules VALUES (?,?,?,?,?,?,?,?,?)',
        schedules,
    )
    conn.commit()
    conn.close()


def _seed_user_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        '''
        CREATE TABLE user_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            device_id TEXT,
            fingerprint TEXT,
            platform TEXT,
            app_version TEXT,
            privacy_consent INTEGER,
            location_consent INTEGER,
            created_at TEXT,
            updated_at TEXT,
            last_active_at TEXT,
            UNIQUE(user_id, fingerprint)
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE user_kyc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            kyc_status TEXT,
            doc_type TEXT,
            doc_number TEXT,
            selfie_url TEXT,
            doc_front_url TEXT,
            doc_back_url TEXT,
            meta_json TEXT,
            reviewer TEXT,
            reviewed_at TEXT,
            created_at TEXT,
            updated_at TEXT,
            UNIQUE(user_id)
        )
        '''
    )
    now = datetime.utcnow().isoformat()
    devices = [
        ('U1', 'device-1', 'fp-1', 'android', '1.0.0', 1, 0, now, now, now),
        ('U3', 'device-7', 'fp-7', 'ios', '1.1.0', 1, 1, now, now, now),
    ]
    conn.executemany(
        'INSERT INTO user_devices (user_id, device_id, fingerprint, platform, app_version, privacy_consent, location_consent, created_at, updated_at, last_active_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
        devices,
    )
    conn.execute(
        'INSERT INTO user_kyc (user_id, kyc_status, doc_type, doc_number, created_at, updated_at) VALUES (?,?,?,?,?,?)',
        ('U1', 'APPROVED', 'ID', 'ID123', now, now),
    )
    conn.commit()
    conn.close()


def _seed_collection_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        '''
        CREATE TABLE collection_cases (
            case_id TEXT PRIMARY KEY,
            loan_id TEXT,
            user_id TEXT,
            bucket TEXT,
            principal_due TEXT,
            currency TEXT,
            status TEXT,
            assigned_to TEXT,
            created_at TEXT,
            updated_at TEXT,
            last_action TEXT,
            ptp_amount TEXT,
            ptp_due_at TEXT,
            resolved_at TEXT,
            notes TEXT
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE collection_actions (
            action_id TEXT PRIMARY KEY,
            case_id TEXT,
            action_type TEXT,
            actor TEXT,
            note TEXT,
            result TEXT,
            ptp_amount TEXT,
            ptp_due_at TEXT,
            created_at TEXT
        )
        '''
    )
    now = datetime.utcnow().isoformat()
    conn.execute(
        'INSERT INTO collection_cases VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        ('CASE1', 'LN123', 'U1', 'D7', '250', 'GHS', 'OPEN', 'collector-1', now, now, 'CALL', '250', now, None, None),
    )
    conn.execute(
        'INSERT INTO collection_cases VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
        ('CASE2', 'LN124', 'U3', 'D30', '800', 'GHS', 'PAID', 'collector-2', now, now, 'SMS', None, None, now, None),
    )
    conn.execute(
        'INSERT INTO collection_actions VALUES (?,?,?,?,?,?,?,?,?)',
        ('ACT1', 'CASE1', 'CALL', 'collector-1', '提醒', 'PTP', '250', now, now),
    )
    conn.execute(
        'INSERT INTO collection_actions VALUES (?,?,?,?,?,?,?,?,?)',
        ('ACT2', 'CASE2', 'SMS', 'collector-2', '催收', None, None, None, now),
    )
    conn.commit()
    conn.close()


def _seed_payment_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        '''
        CREATE TABLE disbursements (
            req_no TEXT PRIMARY KEY,
            loan_id TEXT,
            amount TEXT,
            account_json TEXT,
            channel TEXT,
            status TEXT,
            failure_reason TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        '''
    )
    conn.execute(
        '''
        CREATE TABLE repayments (
            repayment_id TEXT PRIMARY KEY,
            loan_id TEXT,
            amount TEXT,
            currency TEXT,
            channel TEXT,
            txn_ref TEXT,
            status TEXT,
            applied_amount TEXT,
            remaining_due TEXT,
            paid_at TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        '''
    )
    now = datetime.utcnow().isoformat()
    conn.execute(
        'INSERT INTO disbursements VALUES (?,?,?,?,?,?,?,?,?)',
        ('REQ1', 'LN123', '500', '{}', 'mock', 'SUCCESS', None, now, now),
    )
    conn.execute(
        'INSERT INTO repayments VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
        ('RP1', 'LN123', '250', 'GHS', 'mock', 'TXN1', 'POSTED', '250', '250', now, now, now),
    )
    conn.commit()
    conn.close()


def _seed_ledger_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        '''
        CREATE TABLE ledger_entries (
            entry_id TEXT PRIMARY KEY,
            ref_type TEXT,
            ref_id TEXT,
            status TEXT,
            lines_json TEXT,
            created_at TEXT
        )
        '''
    )
    now = datetime.utcnow().isoformat()
    entries = [
        ('LE-1', 'DISBURSEMENT', 'LN123', 'POSTED', '[{"debit":"cash","credit":"loan"}]', now),
        ('LE-2', 'REPAYMENT', 'LN123', 'POSTED', '[{"debit":"loan","credit":"cash"}]', now),
    ]
    conn.executemany('INSERT INTO ledger_entries VALUES (?,?,?,?,?,?)', entries)
    conn.commit()
    conn.close()


def _auth_header(client: TestClient) -> dict:
    resp = client.post('/admin/v1/auth/login', json={'username': 'ops.lead', 'password': 'admin123'})
    token = resp.json()['accessToken']
    return {'Authorization': f'Bearer {token}'}


def test_applications_and_users(client):
    headers = _auth_header(client)
    resp = client.get('/admin/v1/applications', headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data['total'] == 3
    rows = {row['id']: row for row in data['list']}
    assert rows['LN123']['phone'] == '+233-5500-1123'
    assert rows['LN123']['channel'] == 'Google Ads'
    assert '复借' in rows['LN123']['tags']
    loan_id = 'LN123'

    detail = client.get(f'/admin/v1/applications/{loan_id}', headers=headers)
    assert detail.status_code == 200
    assert detail.json()['application']['id'] == 'LN123'
    assert detail.json()['documents'][0]['url'] == 'https://static.local/docs/LN123/id_ocr.pdf'

    user_resp = client.get('/admin/v1/users/U1', headers=headers)
    assert user_resp.status_code == 200
    profile = user_resp.json()
    assert profile['userId'] == 'U1'
    assert profile['loanSummary']['activeLoans'] == 2
    assert float(profile['loanSummary']['outstandingAmount']) == 250.0
    assert profile['device']['platform'] == 'android'
    assert profile['kyc']['status'] == 'APPROVED'
    assert profile['collectionSummary']['openCases'] == 1


def test_collections_and_reports(client):
    headers = _auth_header(client)
    cases_resp = client.get('/admin/v1/collections/cases', headers=headers)
    assert cases_resp.status_code == 200
    assert cases_resp.json()['total'] == 2
    case_id = cases_resp.json()['list'][0]['caseId']

    case_detail = client.get(f'/admin/v1/collections/cases/{case_id}', headers=headers)
    assert case_detail.status_code == 200
    assert case_detail.json()['summary']['caseId'] == 'CASE1'

    stats_resp = client.get('/admin/v1/collections/stats', headers=headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats['totalCases'] == 2
    assert stats['buckets']['D7'] == 1
    assert stats['statuses']['OPEN'] == 1

    due_at = datetime.utcnow().date().isoformat() + 'T00:00:00'
    action_resp = client.post(
        f'/admin/v1/collections/cases/{case_id}/actions',
        headers=headers,
        json={
            'action': 'WHATSAPP',
            'result': 'PROMISE',
            'note': '新PTP',
            'status': 'PROMISE',
            'ptpAmount': 180.0,
            'ptpDueAt': due_at,
        },
    )
    assert action_resp.status_code == 200
    action_detail = action_resp.json()
    assert action_detail['summary']['status'] == 'PROMISE'
    assert action_detail['followUps'][0]['action'] == 'WHATSAPP'
    assert action_detail['ptpRecords'][0]['amount'] == pytest.approx(180.0)
    assert action_detail['ptpRecords'][0]['promiseDate'] == due_at

    dashboard = client.get('/admin/v1/dashboard', headers=headers)
    assert dashboard.status_code == 200
    daily = client.get('/admin/v1/reports/daily', headers=headers)
    assert daily.status_code == 200
    assert daily.json()['total'] >= 1


def test_application_filters(client):
    headers = _auth_header(client)
    resp_repeat_yes = client.get('/admin/v1/applications', headers=headers, params={'repeat': 'yes'})
    assert resp_repeat_yes.status_code == 200
    assert resp_repeat_yes.json()['total'] == 2

    resp_repeat_no = client.get('/admin/v1/applications', headers=headers, params={'repeat': 'no'})
    assert resp_repeat_no.status_code == 200
    assert resp_repeat_no.json()['total'] == 1

    phone_resp = client.get('/admin/v1/applications', headers=headers, params={'phone': '1123'})
    assert phone_resp.status_code == 200
    assert phone_resp.json()['total'] == 1
    assert phone_resp.json()['list'][0]['id'] == 'LN123'

    channel_resp = client.get('/admin/v1/applications', headers=headers, params={'channel': 'Affiliate'})
    assert channel_resp.status_code == 200
    assert channel_resp.json()['total'] == 1
    assert channel_resp.json()['list'][0]['id'] == 'LN124'

    loan_resp = client.get('/admin/v1/applications', headers=headers, params={'loanId': 'LN777'})
    assert loan_resp.status_code == 200
    assert loan_resp.json()['total'] == 1
    assert loan_resp.json()['list'][0]['id'] == 'LN777'

    future = client.get('/admin/v1/applications', headers=headers, params={'startDate': '2099-01-01', 'endDate': '2099-01-02'})
    assert future.status_code == 200
    assert future.json()['total'] == 0

def test_finance_endpoints(client):
    headers = _auth_header(client)
    disb = client.get('/admin/v1/finance/disbursements', headers=headers)
    assert disb.status_code == 200
    assert disb.json()['total'] == 1
    repay = client.get('/admin/v1/finance/repayments', headers=headers)
    assert repay.status_code == 200
    assert repay.json()['list'][0]['txnRef'] == 'TXN1'
    recon = client.get('/admin/v1/finance/reconciliations', headers=headers)
    assert recon.status_code == 200
    assert recon.json()['total'] == 2


def test_collection_action_and_stats(client):
    headers = _auth_header(client)
    stats = client.get('/admin/v1/collections/stats', headers=headers)
    assert stats.status_code == 200
    assert stats.json()['totalCases'] >= 1

    payload = {
        'action': 'CALL',
        'result': 'PTP',
        'note': '用户承诺',
        'ptpAmount': 200,
        'ptpDueAt': '2025-10-25',
        'status': 'PTP'
    }
    resp = client.post('/admin/v1/collections/cases/CASE1/actions', headers=headers, json=payload)
    assert resp.status_code == 200
    detail = resp.json()
    assert detail['summary']['caseId'] == 'CASE1'
    assert detail.get('ptpAmount') is not None
