from datetime import datetime
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

from .config import Settings, get_settings
from .database import init_db, purge_expired_events
from .pipelines import ClickHouseWriter, KafkaEmitter
from .repository import get_event_by_id, insert_event, query_events
from .schemas import AuditEvent, AuditEventCreate, AuditEventList
from .security import verify_service_claims

app = FastAPI(title=get_settings().app_name, version='0.1.0')

EVENT_CREATED_COUNTER = Counter('audit_events_created_total', 'Total number of audit events created')
LIST_LATENCY_HISTOGRAM = Histogram('audit_events_query_duration_seconds', 'Time spent querying audit events')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def startup() -> None:
    init_db()
    purge_expired_events()
    current_settings = get_settings()
    app.state.kafka_emitter = KafkaEmitter(current_settings)
    app.state.clickhouse_writer = ClickHouseWriter(current_settings)


@app.get('/healthz')
def healthz(settings: Settings = Depends(get_settings)) -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.post('/audit/events', status_code=status.HTTP_201_CREATED)
def create_event(event: AuditEventCreate, claims: dict = Depends(verify_service_claims)) -> dict:
    source_service = claims.get('service') or claims.get('sub', 'unknown')
    stored = insert_event(event, source_service)
    EVENT_CREATED_COUNTER.inc()
    payload = stored.model_dump()
    kafka = getattr(app.state, 'kafka_emitter', None)
    if kafka:
        kafka.emit(payload)
    clickhouse = getattr(app.state, 'clickhouse_writer', None)
    if clickhouse:
        clickhouse.write(payload)
    return payload


@app.get('/audit/events', response_model=AuditEventList)
def list_events(
    _: dict = Depends(verify_service_claims),
    actorId: Optional[str] = Query(default=None, min_length=3),
    action: Optional[str] = Query(default=None),
    resourceType: Optional[str] = Query(default=None),
    since: Optional[datetime] = Query(default=None),
    until: Optional[datetime] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=get_settings().max_return_records),
) -> AuditEventList:
    with LIST_LATENCY_HISTOGRAM.time():
        events = query_events(actorId, action, resourceType, since, until, limit)
    return AuditEventList(items=events, total=len(events))


@app.get('/audit/events/{event_id}', response_model=AuditEvent)
def get_event(event_id: str, _: dict = Depends(verify_service_claims)) -> AuditEvent:
    event = get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='event not found')
    return event


@app.get('/metrics')
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
