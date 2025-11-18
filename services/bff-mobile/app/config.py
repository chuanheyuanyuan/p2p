from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', env_prefix='BFF_MOBILE_')

    app_name: str = 'bff-mobile'
    loan_base_url: str = 'http://127.0.0.1:8083'
    payment_base_url: str = 'http://127.0.0.1:8084'
    user_base_url: str = 'http://127.0.0.1:8081'
    http_timeout: float = Field(default=5.0, ge=1, le=60)
    loan_list_limit: int = Field(default=20, ge=1, le=100)
    recommendation_limit: int = Field(default=3, ge=1, le=10)


@lru_cache
def get_settings() -> Settings:
    return Settings()
