from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient

from .config import get_settings
from .routers import dashboard, loans

settings = get_settings()
app = FastAPI(title=settings.app_name, version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(dashboard.router)
app.include_router(loans.router)


@app.on_event('startup')
async def startup() -> None:
    app.state.http_client = AsyncClient(timeout=settings.http_timeout)


@app.on_event('shutdown')
async def shutdown() -> None:
    http_client: AsyncClient = getattr(app.state, 'http_client', None)
    if http_client:
        await http_client.aclose()


@app.get('/healthz')
def healthz() -> dict:
    return {'status': 'ok', 'service': settings.app_name}
