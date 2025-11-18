import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jose import jwt

SERVICE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_ROOT))

from app.config import get_settings
from app.main import app  # noqa: E402  pylint: disable=wrong-import-position

sys.path.insert(0, str(SERVICE_ROOT))
os.environ['OBS_DB_PATH'] = str(SERVICE_ROOT / 'tests' / 'audit-test.db')
os.environ['OBS_JWT_SECRET'] = 'test-jwt-secret'
os.environ['OBS_JWT_ALGORITHM'] = 'HS256'


def issue_token(service: str = 'ops-svc') -> str:
    return jwt.encode({'service': service}, os.environ['OBS_JWT_SECRET'], algorithm=os.environ['OBS_JWT_ALGORITHM'])


@pytest.fixture(autouse=True)
def cleanup_db():
    db_file = Path(os.environ['OBS_DB_PATH'])
    if db_file.exists():
        db_file.unlink()
    get_settings.cache_clear()
    yield
    if db_file.exists():
        db_file.unlink()
    get_settings.cache_clear()


@pytest.fixture()
def api_client():
    with TestClient(app) as client:
        client.headers.update({"Authorization": f"Bearer {issue_token()}"})
        yield client


def test_create_and_list_events(api_client):
    client = api_client
    payload = {
        'actorId': 'ops.lead',
        'actorType': 'ADMIN',
        'action': 'UPDATE_PRODUCT',
        'resourceType': 'PRODUCT',
        'resourceId': 'P1',
        'severity': 'INFO',
        'payload': {'before': 'A', 'after': 'B'},
    }
    resp = client.post('/audit/events', json=payload)
    assert resp.status_code == 201
    event_id = resp.json()['eventId']

    resp = client.get('/audit/events', params={'actorId': 'ops.lead'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['total'] == 1
    assert data['items'][0]['eventId'] == event_id


def test_list_events_filters_by_time_range(api_client):
    client = api_client
    now = datetime.utcnow()
    earlier = (now - timedelta(days=1)).isoformat()
    later = (now + timedelta(minutes=1)).isoformat()
    payload = {
        'actorId': 'system',
        'actorType': 'SERVICE',
        'action': 'PING',
        'resourceType': 'OTEL',
        'resourceId': 'collector',
        'severity': 'INFO',
        'occurredAt': earlier,
    }
    client.post('/audit/events', json=payload)
    resp = client.get('/audit/events', params={'since': now.isoformat()})
    assert resp.status_code == 200
    assert resp.json()['total'] == 0

    resp = client.get('/audit/events', params={'since': earlier, 'until': later})
    assert resp.status_code == 200
    assert resp.json()['total'] == 1


def test_get_event_detail_and_metrics(api_client):
    client = api_client
    payload = {
        'actorId': 'auditor',
        'actorType': 'SERVICE',
        'action': 'EXPORT',
        'resourceType': 'REPORT',
        'resourceId': 'D-1',
        'severity': 'WARN',
    }
    created = client.post('/audit/events', json=payload)
    assert created.status_code == 201
    event_id = created.json()['eventId']

    resp = client.get(f'/audit/events/{event_id}')
    assert resp.status_code == 200
    body = resp.json()
    assert body['actorId'] == 'auditor'
    assert body['resourceId'] == 'D-1'
    assert body['sourceService'] == 'ops-svc'

    metrics_resp = client.get('/metrics')
    assert metrics_resp.status_code == 200
    assert 'audit_events_created_total' in metrics_resp.text


def test_rejects_missing_jwt():
    with TestClient(app) as client:
        resp = client.get('/audit/events')
        assert resp.status_code == 401


def test_pipeline_logs_when_enabled(tmp_path):
    os.environ['OBS_KAFKA_ENABLED'] = 'true'
    os.environ['OBS_CLICKHOUSE_ENABLED'] = 'true'
    os.environ['OBS_KAFKA_LOG_PATH'] = str(tmp_path / 'kafka.log')
    os.environ['OBS_CLICKHOUSE_LOG_PATH'] = str(tmp_path / 'ch.log')
    get_settings.cache_clear()
    payload = {
        'actorId': 'ops.pipeline',
        'actorType': 'SERVICE',
        'action': 'EMIT',
        'resourceType': 'KAFKA',
        'resourceId': 'topic',
    }
    with TestClient(app) as client:
        client.headers.update({"Authorization": f"Bearer {issue_token('pipeline-svc')}"})
        resp = client.post('/audit/events', json=payload)
        assert resp.status_code == 201

    kafka_log = Path(os.environ['OBS_KAFKA_LOG_PATH'])
    clickhouse_log = Path(os.environ['OBS_CLICKHOUSE_LOG_PATH'])
    assert kafka_log.exists()
    assert clickhouse_log.exists()
    assert 'audit.events' in kafka_log.read_text()
    assert 'pipeline-svc' in clickhouse_log.read_text()

    # reset toggles for other tests
    os.environ['OBS_KAFKA_ENABLED'] = 'false'
    os.environ['OBS_CLICKHOUSE_ENABLED'] = 'false'
    get_settings.cache_clear()
