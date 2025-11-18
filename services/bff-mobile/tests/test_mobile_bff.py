import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient
from httpx import Request, Response

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))

os.environ.setdefault('BFF_MOBILE_LOAN_BASE_URL', 'https://loan.test')
os.environ.setdefault('BFF_MOBILE_USER_BASE_URL', 'https://user.test')
os.environ.setdefault('BFF_MOBILE_PAYMENT_BASE_URL', 'https://payment.test')

from app.dependencies import get_http_client
from app.main import app  # noqa: E402  # pylint: disable=wrong-import-position


class StubAsyncClient:
    def __init__(self) -> None:
        self.routes: Dict[Tuple[str, str], Response] = {}
        self.calls: List[Dict[str, Any]] = []

    def add_json_response(self, method: str, url: str, payload: dict, status_code: int = 200) -> None:
        request = Request(method.upper(), url)
        self.routes[(method.upper(), url)] = Response(status_code, json=payload, request=request)

    async def get(self, url: str, params: Optional[dict] = None) -> Response:
        target_url = self._normalize_url(url, params)
        response = self.routes.get(('GET', target_url))
        if response is None:
            raise AssertionError(f'unmocked GET {target_url}')
        self.calls.append({'method': 'GET', 'url': target_url})
        return response

    async def post(self, url: str, json: Optional[dict] = None, headers: Optional[dict] = None) -> Response:
        response = self.routes.get(('POST', url))
        self.calls.append({'method': 'POST', 'url': url, 'json': json, 'headers': headers or {}})
        if response is None:
            raise AssertionError(f'unmocked POST {url}')
        return response

    @staticmethod
    def _normalize_url(url: str, params: Optional[dict]) -> str:
        if not params:
            return url
        ordered = sorted((key, str(value)) for key, value in params.items())
        query = urlencode(ordered)
        return f'{url}?{query}'


@pytest.fixture()
def client() -> Tuple[TestClient, StubAsyncClient]:
    stub = StubAsyncClient()
    app.dependency_overrides[get_http_client] = lambda: stub
    with TestClient(app) as test_client:
        yield test_client, stub
    app.dependency_overrides.clear()


def test_dashboard_returns_metrics(client):
    test_client, stub = client
    user_id = 'borrower-1'
    now = datetime.utcnow().isoformat()
    loans_payload = {
        'items': [
            {
                'loanId': 'LN001',
                'productId': 'P_BASIC',
                'amount': '500.00',
                'termDays': 14,
                'status': 'ACTIVE',
                'outstandingAmount': '150.00',
                'originalAmount': '500.00',
                'lastPaidAt': None,
                'createdAt': now,
                'updatedAt': now,
            }
        ]
    }
    products_payload = {
        'items': [
            {
                'productId': 'P_BASIC',
                'name': '基础贷',
                'currency': 'GHS',
                'amountMin': 100,
                'amountMax': 800,
                'defaultTerm': 14,
                'termOptions': [{'termDays': 14, 'feeRate': 0.15}],
                'enabled': True,
            }
        ]
    }
    stub.add_json_response('GET', 'https://loan.test/users/borrower-1/loans?limit=20', loans_payload)
    stub.add_json_response('GET', 'https://loan.test/loan/products', products_payload)

    resp = test_client.get('/mobile/v1/dashboard', headers={'X-User-Id': user_id})
    assert resp.status_code == 200
    data = resp.json()
    assert data['userId'] == user_id
    assert data['metrics']['activeLoans'] == 1
    assert data['metrics']['totalOutstanding'] == '150.00'
    assert len(data['loans']) == 1
    assert len(data['recommendations']) == 1


def test_create_loan_injects_user_id(client):
    test_client, stub = client
    user_id = 'borrower-2'
    expected_response = {'loanId': 'LN002', 'status': 'DRAFT', 'decision': None, 'score': None}
    stub.add_json_response('POST', 'https://loan.test/loans', expected_response, status_code=201)

    resp = test_client.post(
        '/mobile/v1/loans',
        headers={'X-User-Id': user_id},
        json={'productId': 'P_BASIC', 'amount': 400, 'termDays': 14}
    )
    assert resp.status_code == 201
    assert resp.json() == expected_response
    post_calls = [call for call in stub.calls if call['method'] == 'POST']
    assert post_calls[-1]['json']['userId'] == user_id


def test_list_loans_requires_user_header(client):
    test_client, _ = client
    resp = test_client.get('/mobile/v1/loans')
    assert resp.status_code == 401
