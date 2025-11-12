from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = 'notify-svc'
    default_locale: str = 'en_GH'
    templates_path: Path = Field(default=BASE_DIR / 'templates' / 'catalog.json')
    channel_timeout_seconds: int = 2

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings() -> Settings:
    return Settings()
