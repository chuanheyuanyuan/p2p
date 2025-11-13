from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Query, Response, status

from .database import init_db
from .repository import query_funnel, upsert_attribution
from .schemas import AttributionIn, FunnelResponse, FunnelRow

app = FastAPI(title="channel-svc", version="0.1.0")


@app.on_event('startup')
def startup() -> None:
    init_db()


@app.get('/healthz')
def healthcheck() -> dict:
    return {'status': 'ok'}


@app.post('/channels/attributions', status_code=status.HTTP_204_NO_CONTENT)
def ingest_attribution(
    payload: AttributionIn,
    x_idempotency_key: Optional[str] = Header(default=None, alias='X-Idempotency-Key')
) -> Response:
    try:
        upsert_attribution(payload)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get('/channels/funnel', response_model=FunnelResponse)
def get_funnel(
    startDate: Optional[date] = Query(default=None, description='起始日期（默认近 7 天）'),
    endDate: Optional[date] = Query(default=None, description='结束日期（默认今天）'),
    channel: Optional[str] = Query(default='all', description='渠道标识，默认 all'),
) -> FunnelResponse:
    today = datetime.utcnow().date()
    start_day = startDate or (today - timedelta(days=6))
    end_day = endDate or today
    start_dt = datetime.combine(start_day, datetime.min.time())
    end_dt = datetime.combine(end_day, datetime.max.time())

    rows = query_funnel(start_dt, end_dt, channel)
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
