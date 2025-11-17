from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx

from .config import Settings


@dataclass
class DownstreamClients:
    loan: httpx.AsyncClient
    payment: httpx.AsyncClient
    collection: httpx.AsyncClient
    report: httpx.AsyncClient
    user: httpx.AsyncClient

    async def close(self) -> None:
        await asyncio.gather(
            self.loan.aclose(),
            self.payment.aclose(),
            self.collection.aclose(),
            self.report.aclose(),
            self.user.aclose(),
        )


def build_clients(settings: Settings) -> DownstreamClients:
    timeout = httpx.Timeout(5.0)
    return DownstreamClients(
        loan=httpx.AsyncClient(base_url=settings.loan_base_url, timeout=timeout),
        payment=httpx.AsyncClient(base_url=settings.payment_base_url, timeout=timeout),
        collection=httpx.AsyncClient(base_url=settings.collection_base_url, timeout=timeout),
        report=httpx.AsyncClient(base_url=settings.report_base_url, timeout=timeout),
        user=httpx.AsyncClient(base_url=settings.user_base_url, timeout=timeout),
    )

