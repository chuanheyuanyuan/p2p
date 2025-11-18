import os
import sys
from datetime import datetime
from pathlib import Path

import pytest
import respx
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))

os.environ.setdefault('BFF_MOBILE_LOAN_BASE_URL', 'https://loan.test')
os.environ.setdefault('BFF_MOBILE_USER_BASE_URL', 'https://user.test')
os.environ.setdefault('BFF_MOBILE_PAYMENT_BASE_URL', 'https://payment.test')

from app.main import app  # noqa: E402  pylint: disable=wrong-import-position


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def _loan_payload(now: datetime) -> dict:
    return {
        'loanId': 'LN001',
        'productId': 'P_BASIC',
        'amount': '500.00',
        'termDays': 14,
        'status': 'ACTIVE',
        'outstandingAmount': '150.00',
        'originalAmount': '500.00',
        'createdAt': now.isoformat(),
        'updatedAt': now.isoformat(),
    }


def test_dashboard_flow(client):
    now = datetime.utcnow()
    loans_payload = {'items': [_loan_payload(now)]}
    products_payload = {
        'items': [
            {
                'productId': 'P_BASIC',
                'name': 'Basic Loan',
                'currency': 'GHS',
                 'amountMin': 100,
                'amountMax': 800,
                'defaultTerm': 14,
                'termOptions': [{'termDays': 14, 'feeRate': 0.15}],
                'enabled': True,
            }
        ]
    }
    with respx.mock(assert_all_called=True) as mock:
        mock.get('https://loan.test/users/borrower-1/loans').respond(200, json=loans_payload)
        mock.get('https://loan.test/loan/products').respond(200, json=products_payload)
        resp = client.get('/mobile/v1/dashboard', headers={'X-User-Id': 'borrower-1'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['metrics']['activeLoans'] == 1
    assert len(data['recommendations']) == 1


def test_create_loan_injects_user(client):
    expected = {'loanId': 'LN002', 'status': 'DRAFT', 'decision': None, 'score': None}
    with respx.mock(assert_all_called=True) as mock:
        route = mock.post('https://loan.test/loans').respond(201, json=expected)
        resp = client.post(
            '/mobile/v1/loans',
            headers={'X-User-Id': 'borrower-9'},
            json={'productId': 'P_BASIC', 'amount': 400, 'termDays': 14}
        )
    assert resp.status_code == 201
    assert resp.json() == expected
    body = route.calls.last.request.json()
    assert body['userId'] == 'borrower-9'


def test_requires_user_header(client):
    resp = client.get('/mobile/v1/loans')
    assert resp.status_code == 401
