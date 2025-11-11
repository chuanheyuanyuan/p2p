from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'payment-svc'
    loan_svc_base_url: str = 'http://localhost:8083'
    loan_svc_timeout: float = 3.0

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings() -> Settings:
    return Settings()
