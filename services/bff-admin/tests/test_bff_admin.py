from importlib import reload
from pathlib import Path
import sqlite3
import sys
from datetime import datetime

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
    products_path = tmp_path / 'products.json'

    _seed_loan_db(loan_db)
    _seed_user_db(user_db)
    _seed_collection_db(collection_db)
    _seed_payment_db(payment_db)
    products_path.write_text('[{"productId":"P_BASIC","name":"InsCash Basic"}]', encoding='utf-8')

    monkeypatch.setenv('BFF_ADMIN_LOAN_DB_PATH', str(loan_db))
    monkeypatch.setenv('BFF_ADMIN_USER_DB_PATH', str(user_db))
    monkeypatch.setenv('BFF_ADMIN_COLLECTION_DB_PATH', str(collection_db))
    monkeypatch.setenv('BFF_ADMIN_PAYMENT_DB_PATH', str(payment_db))

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
    conn.execute(
        'INSERT INTO loan_applications VALUES (?,?,?,?,?,?,?,?,?,?)',
        (
            'LN123',
            'U1',
            'P_BASIC',
            500,
            7,
            'SUBMITTED',
            now,
            now,
            'AUTO_PASS',
            720,
        ),
    )
    conn.execute(
        'INSERT INTO repayment_schedules VALUES (?,?,?,?,?,?,?,?,?)',
        ('LN123', 'GHS', '500', '250', '250', 'ACTIVE', now, now, now),
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
    conn.execute(
        'INSERT INTO user_devices (user_id, device_id, fingerprint, platform, app_version, privacy_consent, location_consent, created_at, updated_at, last_active_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
        ('U1', 'device-1', 'fp-1', 'android', '1.0.0', 1, 0, now, now, now),
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
        'INSERT INTO collection_actions VALUES (?,?,?,?,?,?,?,?,?)',
        ('ACT1', 'CASE1', 'CALL', 'collector-1', '提醒', 'PTP', '250', now, now),
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


def _auth_header(client: TestClient) -> dict:
    resp = client.post('/admin/v1/auth/login', json={'username': 'ops.lead', 'password': 'admin123'})
    token = resp.json()['accessToken']
    return {'Authorization': f'Bearer {token}'}


def test_applications_and_users(client):
    headers = _auth_header(client)
    resp = client.get('/admin/v1/applications', headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data['total'] == 1
    loan_id = data['list'][0]['id']

    detail = client.get(f'/admin/v1/applications/{loan_id}', headers=headers)
    assert detail.status_code == 200
    assert detail.json()['application']['id'] == 'LN123'

    user_resp = client.get('/admin/v1/users/U1', headers=headers)
    assert user_resp.status_code == 200
    assert user_resp.json()['userId'] == 'U1'


def test_collections_and_reports(client):
    headers = _auth_header(client)
    cases_resp = client.get('/admin/v1/collections/cases', headers=headers)
    assert cases_resp.status_code == 200
    assert cases_resp.json()['total'] == 1
    case_id = cases_resp.json()['list'][0]['caseId']

    case_detail = client.get(f'/admin/v1/collections/cases/{case_id}', headers=headers)
    assert case_detail.status_code == 200
    assert case_detail.json()['summary']['caseId'] == 'CASE1'

    dashboard = client.get('/admin/v1/dashboard', headers=headers)
    assert dashboard.status_code == 200
    daily = client.get('/admin/v1/reports/daily', headers=headers)
    assert daily.status_code == 200
    assert daily.json()['total'] >= 1
