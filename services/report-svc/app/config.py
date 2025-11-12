from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
SERVICES_DIR = BASE_DIR.parent


class Settings(BaseSettings):
    app_name: str = 'report-svc'
    default_currency: str = 'GHS'
    data_store_path: Path = Field(default=BASE_DIR / 'report.db')
    loan_db_path: Path = Field(default=SERVICES_DIR / 'loan-svc' / 'loan.db')
    payment_db_path: Path = Field(default=SERVICES_DIR / 'payment-svc' / 'payment.db')
    collection_db_path: Path = Field(default=SERVICES_DIR / 'collection-svc' / 'collection.db')
    ledger_db_path: Path = Field(default=SERVICES_DIR / 'ledger-svc' / 'ledger.db')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings() -> Settings:
    return Settings()
