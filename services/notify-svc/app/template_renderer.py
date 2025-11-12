from decimal import Decimal
from typing import Any, Dict

from babel.dates import format_datetime
from babel.numbers import format_currency
from jinja2 import Environment, StrictUndefined


def render_template(body: str, variables: Dict[str, Any], locale: str, currency: str) -> str:
    env = Environment(undefined=StrictUndefined, autoescape=False)
    env.filters['currency'] = lambda value, code=None: _currency_filter(value, code or currency, locale)
    env.filters['datetime'] = lambda value, fmt='medium': format_datetime(value, format=fmt, locale=locale)
    template = env.from_string(body)
    return template.render(**variables)


def _currency_filter(value: Any, currency_code: str, locale: str) -> str:
    numeric = Decimal(str(value))
    return format_currency(numeric, currency_code, locale=locale)
