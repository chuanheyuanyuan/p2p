from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
SERVICES_DIR = BASE_DIR.parent


class AdminUser(BaseModel):
    id: str
    username: str
    password: str
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    displayName: str
    email: str
    title: Optional[str] = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='BFF_ADMIN_',
        json_encoders={Path: str},
    )

    app_name: str = 'bff-admin'
    loan_base_url: str = 'http://127.0.0.1:8083'
    payment_base_url: str = 'http://127.0.0.1:8084'
    collection_base_url: str = 'http://127.0.0.1:8086'
    report_base_url: str = 'http://127.0.0.1:8012'
    user_base_url: str = 'http://127.0.0.1:8081'
    jwt_secret: str = 'admin-bff-secret'
    jwt_algorithm: str = 'HS256'
    session_ttl_seconds: int = 3600
    allow_origins: List[str] = Field(default_factory=lambda: ['*'])
    admin_users: List[AdminUser] = Field(
        default_factory=lambda: [
            AdminUser(
                id='staff-ops-01',
                username='ops.lead',
                password='admin123',
                roles=['ADMIN', 'OPS_MANAGER', 'ANALYST'],
                permissions=['applications:read', 'reports:view', 'ops:write'],
                displayName='Ops Lead',
                email='ops.lead@inscash.com',
                title='运营负责人',
            ),
            AdminUser(
                id='staff-collector-07',
                username='collector.jr',
                password='collector123',
                roles=['COLLECTION'],
                permissions=['collections:workbench'],
                displayName='Collector JR',
                email='collector.jr@inscash.com',
                title='D1 坐席',
            ),
            AdminUser(
                id='staff-analyst-03',
                username='analyst',
                password='analyst123',
                roles=['ANALYST'],
                permissions=['reports:view'],
                displayName='Data Analyst',
                email='analyst@inscash.com',
                title='数据分析师',
            ),
        ]
    )
    loan_db_path: Path = Field(default=SERVICES_DIR / 'loan-svc' / 'loan.db')
    payment_db_path: Path = Field(default=SERVICES_DIR / 'payment-svc' / 'payment.db')
    collection_db_path: Path = Field(default=SERVICES_DIR / 'collection-svc' / 'collection.db')
    user_db_path: Path = Field(default=SERVICES_DIR / 'user-svc' / 'user.db')
    max_application_rows: int = 1000

@lru_cache
def get_settings() -> Settings:
    return Settings()
