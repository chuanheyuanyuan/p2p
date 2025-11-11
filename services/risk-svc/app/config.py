from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'risk-svc'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings() -> Settings:
    return Settings()
