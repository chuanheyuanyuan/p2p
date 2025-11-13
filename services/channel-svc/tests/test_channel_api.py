from datetime import datetime, timedelta
from importlib import import_module
from pathlib import Path
import sys
import types

import pytest
from fastapi.testclient import TestClient

SERVICE_ROOT = Path(__file__).resolve().parents[2] / 'channel-svc'
PACKAGE_PATH = SERVICE_ROOT / 'app'
app_pkg = types.ModuleType('app')
app_pkg.__path__ = [str(PACKAGE_PATH)]
app_pkg.__package__ = 'app'
sys.modules['app'] = app_pkg
sys.path.insert(0, str(SERVICE_ROOT))


def reload_app_modules():
    for module in list(sys.modules.keys()):
        if module.startswith('app.'):
            del sys.modules[module]
    config = import_module('app.config')
    database = import_module('app.database')
    main = import_module('app.main')
    return config, database, main


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / 'channel.db'
    monkeypatch.setenv('CHANNEL_DB_PATH', str(db_path))
    _, _, main = reload_app_modules()
    with TestClient(main.app) as test_client:
        yield test_client


def build_payload(install_id: str, event: str, minutes_offset: int = 0, cost: str = '0') -> dict:
    occurred = datetime.utcnow() + timedelta(minutes=minutes_offset)
    return {
        'installId': install_id,
        'channel': 'facebook',
        'campaign': 'FB-Q4',
        'event': event,
        'cost': cost,
        'occurredAt': occurred.isoformat() + 'Z',
    }


def test_ingest_and_funnel_flow(client):
    for idx, event in enumerate(['install', 'register', 'apply', 'disburse']):
        resp = client.post('/channels/attributions', json=build_payload('install-1', event, idx))
        assert resp.status_code == 204

    resp = client.get('/channels/funnel')
    assert resp.status_code == 200
    data = resp.json()
    assert data['total'] >= 1
    first_row = data['items'][0]
    assert first_row['installs'] == 1
    assert first_row['registrations'] == 1
    assert first_row['applications'] == 1
    assert first_row['disbursements'] == 1


def test_duplicate_ingest_is_idempotent(client):
    payload = build_payload('install-dup', 'install', cost='1.5')
    resp1 = client.post('/channels/attributions', json=payload)
    resp2 = client.post('/channels/attributions', json=payload)
    assert resp1.status_code == 204
    assert resp2.status_code == 204

    resp = client.get('/channels/funnel', params={'channel': 'facebook'})
    assert resp.status_code == 200
    row = resp.json()['items'][0]
    assert row['installs'] == 1
