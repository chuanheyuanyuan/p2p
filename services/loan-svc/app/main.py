from fastapi import FastAPI, Query
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .schemas import ProductListResponse
from .service import filter_products, load_products

settings = get_settings()
app = FastAPI(title='loan-svc', version='0.1.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/healthz')
def healthz() -> dict:
    try:
        load_products()
        status_msg = 'ok'
    except Exception as exc:
        status_msg = f'error: {exc}'
    return {'status': status_msg, 'service': settings.app_name}


@app.get('/loan/products', response_model=ProductListResponse)
def get_products(productId: Optional[str] = Query(default=None)) -> ProductListResponse:
    items = filter_products(productId)
    return ProductListResponse(items=items)
