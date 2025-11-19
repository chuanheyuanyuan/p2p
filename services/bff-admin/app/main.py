from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .admin_store import initialize_admin_store
from .application_profiles import ensure_application_profiles
from .config import get_settings
from .routers import applications, auth, collections, finance, reports, users

settings = get_settings()
app = FastAPI(title='bff-admin', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(users.router)
app.include_router(collections.router)
app.include_router(finance.router)
app.include_router(reports.router)


@app.on_event('startup')
def _startup() -> None:
    initialize_admin_store(settings)
    ensure_application_profiles(settings)


@app.get('/healthz')
def healthz() -> dict:
    return {'status': 'ok', 'service': settings.app_name}
