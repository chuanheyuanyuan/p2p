import json
from typing import List, Optional
from fastapi import HTTPException, status

from .config import get_settings
from .schemas import Product

settings = get_settings()
_cache: Optional[List[Product]] = None


def load_products(force: bool = False) -> List[Product]:
    global _cache
    if _cache is not None and not force:
        return _cache
    if not settings.products_path.exists():
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='products config missing')
    data = json.loads(settings.products_path.read_text(encoding='utf-8'))
    _cache = [Product(**item) for item in data]
    return _cache


def filter_products(product_id: Optional[str]) -> List[Product]:
    products = load_products()
    if product_id:
        products = [p for p in products if p.productId == product_id]
    return [p for p in products if p.enabled]
