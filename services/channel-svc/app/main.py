from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status

from .database import init_db
from .repository import upsert_attribution, query_funnel
from .schemas import AttributionAccepted, AttributionIn, FunnelResponse, FunnelRow

app = FastAPI(title="channel-svc", version="0.1.0")


@app.on_event('startup')
def startup() -> None:
    init_db()


@app.get('/healthz')
def healthcheck() -> dict:
    return {'status': 'ok'}


@app.post('/channels/attributions', status_code=status.HTTP_202_ACCEPTED, response_model=AttributionAccepted)
def ingest_attribution(payload: AttributionIn, x_idempotency_key: Optional[str] = Header(default=None)) -> AttributionAccepted:
    try:
        upsert_attribution(payload)
        return AttributionAccepted(installId=payload.installId, event=payload.event)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc))


@app.get('/channels/funnel', response_model=FunnelResponse)
def get_funnel(startDate: Optional[datetime] = None, endDate: Optional[datetime] = None, channel: Optional[str] = 'all') -> FunnelResponse:
    start = startDate or datetime.utcnow() - timedelta(days=7)
    end = endDate or datetime.utcnow()
    rows = query_funnel(start, end, channel)
    items = [
        FunnelRow(
            date=row['stat_date'],
            channel=row['channel'],
            installs=row['installs'],
            registrations=row['registrations'],
            applications=row['applications'],
            disbursements=row['disbursements'],
            spend=row['spend'],
        )
        for row in rows
    ]
    return FunnelResponse(items=items, total=len(items))
