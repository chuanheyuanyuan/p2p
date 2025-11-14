from importlib import reload
from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))

ADMIN_HEADERS = {'X-Admin-Token': 'admin-token', 'Content-Type': 'application/json'}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / 'ops.db'
    monkeypatch.setenv('OPS_DB_PATH', str(db_path))

    import app.main as main

    reload(main)

    with TestClient(main.app) as test_client:
        yield test_client


def test_product_lifecycle(client):
    payload = {
        'productId': 'P_TEST',
        'name': 'Test Product',
        'description': 'Ops config',
        'config': '{"limit":"1000"}',
    }
    resp = client.post('/ops/products', json=payload, headers=ADMIN_HEADERS)
    assert resp.status_code == 201
    prod = resp.json()
    assert prod['version'] == 1

    resp = client.get('/ops/products', headers=ADMIN_HEADERS)
    assert resp.status_code == 200
    assert any(item['productId'] == 'P_TEST' for item in resp.json())

    update_resp = client.put(
        '/ops/products/P_TEST', json={'config': '{"limit":"2000"}'}, headers=ADMIN_HEADERS
    )
    assert update_resp.status_code == 200
    assert update_resp.json()['version'] == 2

    delete_resp = client.delete('/ops/products/P_TEST', headers=ADMIN_HEADERS)
    assert delete_resp.status_code == 204


def test_grade_rule_and_audit(client):
    grade_payload = {'gradeId': 'G_OPS', 'label': 'Ops Grade', 'criteria': 'score>700'}
    rule_payload = {
        'ruleId': 'R_OPS',
        'name': 'Ops Rule',
        'condition': 'amount<500',
        'action': 'auto_approve',
        'active': True,
    }

    grade_resp = client.post('/ops/grades', json=grade_payload, headers=ADMIN_HEADERS)
    assert grade_resp.status_code == 200
    assert grade_resp.json()['label'] == 'Ops Grade'

    rule_resp = client.post('/ops/rules', json=rule_payload, headers=ADMIN_HEADERS)
    assert rule_resp.status_code == 200
    assert rule_resp.json()['ruleId'] == 'R_OPS'

    reload_resp = client.post('/ops/reload', headers=ADMIN_HEADERS)
    assert reload_resp.status_code == 202

    audit_resp = client.get('/ops/audit', headers=ADMIN_HEADERS)
    assert audit_resp.status_code == 200
    assert len(audit_resp.json()) >= 1
