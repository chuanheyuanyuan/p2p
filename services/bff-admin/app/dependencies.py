from fastapi import Request

from .config import get_settings, Settings
from .downstream import DownstreamClients


def get_app_settings() -> Settings:
    return get_settings()


def get_clients(request: Request) -> DownstreamClients:
    clients = getattr(request.app.state, 'clients', None)
    if not clients:
        raise RuntimeError('Downstream clients 未初始化')
    return clients

