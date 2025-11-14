from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file='.env', env_file_encoding='utf-8', env_prefix='OPS_')

    app_name: str = 'ops-svc'
    db_path: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / 'ops.db')
    admin_token: str = Field(default='admin-token')


@lru_cache
def get_settings() -> Settings:
    return Settings()
