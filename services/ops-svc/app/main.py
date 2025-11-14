from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .repository import (
    delete_product,
    insert_product,
    list_products,
    list_grades,
    list_rules,
    list_audits,
    record_audit,
    update_product,
    upsert_grade,
    upsert_rule,
)
from .schemas import (
    AuditLogOut,
    GradeIn,
    GradeOut,
    ProductCreate,
    ProductOut,
    ProductUpdate,
    RuleIn,
    RuleOut,
)

settings = get_settings()


@asynccontextmanager
async def _lifespan(_: FastAPI):
    from .database import init_db

    init_db()
    yield


app = FastAPI(title=settings.app_name, version='0.1.0', lifespan=_lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])


def require_admin(token: str = Header(default='', alias='X-Admin-Token')) -> str:
    if token != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid admin token')
    return 'ops-admin'


def _product_out(row: dict) -> ProductOut:
    return ProductOut(
        productId=row['product_id'],
        name=row['name'],
        description=row['description'],
        version=row['version'],
        config=row['config'],
        createdAt=row['created_at'],
        updatedAt=row['updated_at'],
    )


def _grade_out(row: dict) -> GradeOut:
    return GradeOut(
        gradeId=row['grade_id'],
        label=row['label'],
        criteria=row['criteria'],
        createdAt=row['created_at'],
        updatedAt=row['updated_at'],
    )


def _rule_out(row: dict) -> RuleOut:
    return RuleOut(
        ruleId=row['rule_id'],
        name=row['name'],
        condition=row['condition'],
        action=row['action'],
        active=bool(row['active']),
        createdAt=row['created_at'],
        updatedAt=row['updated_at'],
    )


def _audit_out(row: dict) -> AuditLogOut:
    return AuditLogOut(
        auditId=row['audit_id'],
        entityType=row['entity_type'],
        entityId=row['entity_id'],
        action=row['action'],
        actor=row['actor'],
        payload=row.get('payload'),
        createdAt=row['created_at'],
    )



@app.post('/ops/products', response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, actor: str = Depends(require_admin)) -> ProductOut:
    record = insert_product(payload)
    record_audit('product', payload.productId, 'create', actor, payload.model_dump_json())
    return _product_out(record)


@app.get('/ops/products', response_model=list[ProductOut])
def get_products(actor: str = Depends(require_admin)) -> list[ProductOut]:
    return [_product_out(row) for row in list_products()]


@app.put('/ops/products/{product_id}', response_model=ProductOut)
def update_product_endpoint(
    product_id: str, payload: ProductUpdate, actor: str = Depends(require_admin)
) -> ProductOut:
    record = update_product(product_id, payload.model_dump(exclude_none=True))
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='product not found')
    record_audit('product', product_id, 'update', actor, payload.model_dump_json(exclude_none=True))
    return _product_out(record)


@app.delete('/ops/products/{product_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(product_id: str, actor: str = Depends(require_admin)) -> None:
    delete_product(product_id)
    record_audit('product', product_id, 'delete', actor)


@app.post('/ops/grades', response_model=GradeOut)
def upsert_grade_endpoint(payload: GradeIn, actor: str = Depends(require_admin)) -> GradeOut:
    grade = upsert_grade(payload)
    record_audit('grade', payload.gradeId, 'upsert', actor, payload.model_dump_json())
    return _grade_out(grade)


@app.get('/ops/grades', response_model=list[GradeOut])
def list_grades_endpoint(actor: str = Depends(require_admin)) -> list[GradeOut]:
    return [_grade_out(row) for row in list_grades()]


@app.post('/ops/rules', response_model=RuleOut)
def upsert_rule_endpoint(payload: RuleIn, actor: str = Depends(require_admin)) -> RuleOut:
    rule = upsert_rule(payload)
    record_audit('rule', payload.ruleId, 'upsert', actor, payload.model_dump_json())
    return _rule_out(rule)


@app.get('/ops/rules', response_model=list[RuleOut])
def list_rules_endpoint(actor: str = Depends(require_admin)) -> list[RuleOut]:
    return [_rule_out(row) for row in list_rules()]


@app.post('/ops/reload', status_code=status.HTTP_202_ACCEPTED)
def reload_configs(actor: str = Depends(require_admin)) -> dict:
    record_audit('ops', 'reload', 'reload', actor)
    return {'status': 'reloaded'}


@app.get('/ops/audit', response_model=list[AuditLogOut])
def audit_logs(actor: str = Depends(require_admin)) -> list[AuditLogOut]:
    return [_audit_out(row) for row in list_audits()]
