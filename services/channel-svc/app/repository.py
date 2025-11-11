from datetime import datetime
from typing import Iterable, List

from .database import get_conn
from .schemas import AttributionIn


def upsert_attribution(payload: AttributionIn) -> None:
    sql = (
        "INSERT INTO channel_attributions (install_id, channel, campaign, event, cost, occurred_at) "
        "VALUES (?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(install_id, event) DO UPDATE SET "
        "channel=excluded.channel, campaign=excluded.campaign, cost=excluded.cost, occurred_at=excluded.occurred_at"
    )
    with get_conn() as conn:
        conn.execute(
            sql,
            (payload.installId, payload.channel, payload.campaign, payload.event, payload.cost, payload.occurredAt.isoformat()),
        )


def query_funnel(start: datetime, end: datetime, channel: str | None = None) -> List[dict]:
    conditions = ["occurred_at BETWEEN ? AND ?"]
    params: List = [start.isoformat(), end.isoformat()]
    if channel and channel.lower() != 'all':
        conditions.append("channel = ?")
        params.append(channel)
    where_clause = " AND ".join(conditions)

    sql = f"""
    SELECT
        DATE(occurred_at) as stat_date,
        channel,
        SUM(CASE WHEN event='install' THEN 1 ELSE 0 END) as installs,
        SUM(CASE WHEN event='register' THEN 1 ELSE 0 END) as registrations,
        SUM(CASE WHEN event='apply' THEN 1 ELSE 0 END) as applications,
        SUM(CASE WHEN event='disburse' THEN 1 ELSE 0 END) as disbursements,
        SUM(CASE WHEN event='install' THEN cost ELSE 0 END) as spend
    FROM channel_attributions
    WHERE {where_clause}
    GROUP BY stat_date, channel
    ORDER BY stat_date DESC, channel
    """

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
