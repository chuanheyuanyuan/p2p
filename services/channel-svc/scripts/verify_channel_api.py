#!/usr/bin/env python3
"""Quick verification script for channel-svc endpoints."""
from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
from typing import Iterable

import httpx

BASE_URL = os.getenv('CHANNEL_BASE_URL', 'http://localhost:8011')


def _post_attribution(client: httpx.Client, payload: dict) -> None:
    resp = client.post(f'{BASE_URL}/channels/attributions', json=payload, timeout=5)
    resp.raise_for_status()


def _build_payload(install_id: str, event: str, offset_minutes: int, cost: str = '0') -> dict:
    occurred = datetime.utcnow() + timedelta(minutes=offset_minutes)
    return {
        'installId': install_id,
        'channel': 'facebook',
        'campaign': 'FB-Q4',
        'event': event,
        'cost': cost,
        'occurredAt': occurred.isoformat() + 'Z',
    }


def _verify_funnel(client: httpx.Client) -> None:
    today = datetime.utcnow().date()
    params = {
        'startDate': (today - timedelta(days=1)).isoformat(),
        'endDate': today.isoformat(),
        'channel': 'facebook',
    }
    resp = client.get(f'{BASE_URL}/channels/funnel', params=params, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    if data['total'] == 0:
        raise RuntimeError('Funnel query returned no rows')
    row = data['items'][0]
    for key in ['installs', 'registrations', 'applications', 'disbursements']:
        if row[key] < 1:
            raise RuntimeError(f'Funnel field {key} expected >= 1, got {row[key]}')
    print('Funnel sample:', row)


def main() -> None:
    print(f'Verifying channel-svc at {BASE_URL}')
    events: Iterable[str] = ['install', 'register', 'apply', 'disburse']
    with httpx.Client() as client:
        for idx, event in enumerate(events):
            payload = _build_payload('install-verify', event, idx * 5, cost='1.50' if event == 'install' else '0')
            _post_attribution(client, payload)
            print(f'  ✔ posted {event}')
        _verify_funnel(client)
    print('All verifications passed ✅')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f'[ERROR] {exc}', file=sys.stderr)
        sys.exit(1)
