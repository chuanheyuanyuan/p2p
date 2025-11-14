from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    productId: str
    name: str
    description: Optional[str] = None
    config: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[str] = None


class ProductOut(BaseModel):
    productId: str
    name: str
    description: Optional[str]
    version: int
    config: str
    createdAt: datetime
    updatedAt: datetime


class GradeIn(BaseModel):
    gradeId: str
    label: str
    criteria: str


class GradeOut(BaseModel):
    gradeId: str
    label: str
    criteria: str
    createdAt: datetime
    updatedAt: datetime


class RuleIn(BaseModel):
    ruleId: str
    name: str
    condition: str
    action: str
    active: Optional[bool] = True


class RuleOut(BaseModel):
    ruleId: str
    name: str
    condition: str
    action: str
    active: bool
    createdAt: datetime
    updatedAt: datetime


class AuditLogOut(BaseModel):
    auditId: int
    entityType: str
    entityId: str
    action: str
    actor: str
    payload: Optional[str]
    createdAt: datetime
