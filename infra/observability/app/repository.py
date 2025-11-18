from datetime import datetime
from typing import List, Optional
from uuid import uuid4
import json

from .database import get_connection
from .schemas import AuditEventCreate, AuditEvent


def insert_event(payload: AuditEventCreate, source_service: str) -> AuditEvent:
    event_id = str(uuid4())
    recorded_at = datetime.utcnow().isoformat()
    payload_dict = payload.model_dump()
    payload_json = json.dumps(payload_dict.get('payload') or {})
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO audit_events (
                event_id, actor_id, actor_type, action,
                resource_type, resource_id, severity, payload,
                ip_address, user_agent, occurred_at, recorded_at, source_service
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                event_id,
                payload.actorId,
                payload.actorType,
                payload.action,
                payload.resourceType,
                payload.resourceId,
                payload.severity,
                payload_json,
                payload.ipAddress,
                payload.userAgent,
                payload.occurredAt.isoformat(),
                recorded_at,
                source_service,
            )
        )
        conn.commit()
    return AuditEvent(
        eventId=event_id,
        recordedAt=recorded_at,
        actorId=payload.actorId,
        actorType=payload.actorType,
        action=payload.action,
        resourceType=payload.resourceType,
        resourceId=payload.resourceId,
        severity=payload.severity,
        payload=json.loads(payload_json),
        ipAddress=payload.ipAddress,
        userAgent=payload.userAgent,
        occurredAt=payload.occurredAt,
        sourceService=source_service
    )


def get_event_by_id(event_id: str) -> Optional[AuditEvent]:
    with get_connection() as conn:
        row = conn.execute('SELECT * FROM audit_events WHERE event_id = ?', (event_id,)).fetchone()
    if not row:
        return None
    return AuditEvent(
        eventId=row['event_id'],
        actorId=row['actor_id'],
        actorType=row['actor_type'],
        action=row['action'],
        resourceType=row['resource_type'],
        resourceId=row['resource_id'],
        severity=row['severity'],
        payload=json.loads(row['payload'] or '{}'),
        ipAddress=row['ip_address'],
        userAgent=row['user_agent'],
        occurredAt=datetime.fromisoformat(row['occurred_at']),
        recordedAt=row['recorded_at'],
        sourceService=row['source_service'],
    )


def query_events(
    actor_id: Optional[str],
    action: Optional[str],
    resource_type: Optional[str],
    since: Optional[datetime],
    until: Optional[datetime],
    limit: int,
) -> List[AuditEvent]:
    query = 'SELECT * FROM audit_events WHERE 1=1'
    params: List[str] = []
    if actor_id:
        query += ' AND actor_id = ?'
        params.append(actor_id)
    if action:
        query += ' AND action = ?'
        params.append(action)
    if resource_type:
        query += ' AND resource_type = ?'
        params.append(resource_type)
    if since:
        query += ' AND occurred_at >= ?'
        params.append(since.isoformat())
    if until:
        query += ' AND occurred_at <= ?'
        params.append(until.isoformat())
    query += ' ORDER BY occurred_at DESC LIMIT ?'
    params.append(str(limit))
    events: List[AuditEvent] = []
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        for row in rows:
            events.append(
                AuditEvent(
                    eventId=row['event_id'],
                    actorId=row['actor_id'],
                    actorType=row['actor_type'],
                    action=row['action'],
                    resourceType=row['resource_type'],
                    resourceId=row['resource_id'],
                    severity=row['severity'],
                    payload=json.loads(row['payload'] or '{}'),
                    ipAddress=row['ip_address'],
                    userAgent=row['user_agent'],
                    occurredAt=datetime.fromisoformat(row['occurred_at']),
                    recordedAt=row['recorded_at'],
                    sourceService=row['source_service'],
                )
            )
    return events
