#!/usr/bin/env python3
"""CLI helper to verify ops-svc endpoints."""
from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Iterable

import httpx

BASE_URL = os.getenv('OPS_BASE_URL', 'http://localhost:8021')
ADMIN_TOKEN = os.getenv('OPS_ADMIN_TOKEN', 'admin-token')
HEADERS = {'X-Admin-Token': ADMIN_TOKEN, 'Content-Type': 'application/json'}


def _post(path: str, payload: dict) -> httpx.Response:
    resp = httpx.post(f'{BASE_URL}{path}', json=payload, headers=HEADERS, timeout=5)
    resp.raise_for_status()
    return resp


def _reload() -> httpx.Response:
    return httpx.post(f'{BASE_URL}/ops/reload', headers=HEADERS, timeout=5)


def _audit() -> list[dict]:
    resp = httpx.get(f'{BASE_URL}/ops/audit', headers=HEADERS, timeout=5)
    resp.raise_for_status()
    return resp.json()


def _build_product(install_id: str) -> dict:
    return {
        'productId': f'P_{install_id}',
        'name': f'Product {install_id}',
        'description': 'auto-generated',
        'config': f'{{"max": "{1000 + len(install_id)}"}}',
    }


def main() -> None:
    print(f'Verifying ops-svc API at {BASE_URL}')
    product = _build_product('verify')
    _post('/ops/products', product)
    print('  ✔ created product')
    resp = httpx.put(f"{BASE_URL}/ops/products/{product['productId']}", json={'config': '{"max":"2000"}'}, headers=HEADERS, timeout=5)
    resp.raise_for_status()
    print('  ✔ updated product')
    grade = {
        'gradeId': 'G_OPS',
        'label': 'Ops Grade',
        'criteria': 'score>700'
    }
    _post('/ops/grades', grade)
    print('  ✔ upserted grade')
    rule = {
        'ruleId': 'R_OPS_AUTOMATE',
        'name': 'Ops Rule',
        'condition': 'amount<500',
        'action': 'auto_approve',
        'active': True
    }
    _post('/ops/rules', rule)
    print('  ✔ upserted rule')
    _reload()
    print('  ✔ reload triggered')
    audits = _audit()
    if not audits:
        raise RuntimeError('no audit logs found')
    print(f'  ✔ audit log entries: {len(audits)}')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'[ERROR] {exc}', file=sys.stderr)
        sys.exit(1)
