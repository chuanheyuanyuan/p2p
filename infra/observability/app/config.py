from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', env_prefix='OBS_')

    app_name: str = 'observability-svc'
    db_path: Path = Field(default=BASE_DIR / 'audit.db')
    retention_days: int = Field(default=90, ge=7, le=365)
    max_return_records: int = Field(default=200, ge=50, le=500)
    jwt_secret: str = Field(default='obs-jwt-secret')
    jwt_algorithm: str = Field(default='HS256')
    kafka_enabled: bool = Field(default=False)
    kafka_log_path: Path = Field(default=BASE_DIR / 'kafka-events.log')
    kafka_topic: str = Field(default='audit.events')
    clickhouse_enabled: bool = Field(default=False)
    clickhouse_log_path: Path = Field(default=BASE_DIR / 'clickhouse-events.log')


@lru_cache
def get_settings() -> Settings:
    return Settings()
