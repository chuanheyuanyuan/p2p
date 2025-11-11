from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = 'auth-svc'
    redis_url: Optional[str] = Field(default=None, description='Redis connection string')
    otp_code_length: int = 6
    otp_ttl_seconds: int = 300
    otp_rate_limit_count: int = 3
    otp_rate_limit_window_seconds: int = 900
    otp_allowed_channels: list[str] = Field(default_factory=lambda: ['sms', 'whatsapp'])
    otp_code_secret: str = Field(default='inscash-secret-key', description='Used to hash OTP codes')
    jwt_secret: str = Field(default='inscash-jwt-secret')
    jwt_algorithm: str = 'HS256'
    jwt_access_ttl_seconds: int = 900
    jwt_refresh_ttl_seconds: int = 2592000  # 30 days

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings() -> Settings:
    return Settings()
