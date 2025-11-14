from datetime import datetime
from typing import Dict, List, Optional

from .database import get_conn
from .schemas import GradeIn, ProductCreate, RuleIn


def _now() -> str:
    return datetime.utcnow().isoformat()


def _row_to_dict(row) -> Dict[str, str]:
    return dict(row) if row else {}


def insert_product(product: ProductCreate) -> Dict[str, str]:
    now = _now()
    with get_conn() as conn:
        conn.execute(
            '''
            INSERT INTO ops_products (product_id, name, description, config, version, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (product.productId, product.name, product.description, product.config, 1, now, now)
        )
    return get_product(product.productId)


def get_product(product_id: str) -> Dict[str, str]:
    with get_conn() as conn:
        row = conn.execute('SELECT * FROM ops_products WHERE product_id = ?', (product_id,)).fetchone()
    return _row_to_dict(row)


def update_product(product_id: str, payload: Dict[str, str]) -> Dict[str, str]:
    existing = get_product(product_id)
    if not existing:
        return {}
    version = existing['version'] + 1
    now = _now()
    with get_conn() as conn:
        conn.execute(
            '''
            UPDATE ops_products
            SET name = ?, description = ?, config = ?, version = ?, updated_at = ?
            WHERE product_id = ?
            ''',
            (
                payload.get('name', existing['name']),
                payload.get('description', existing['description']),
                payload.get('config', existing['config']),
                version,
                now,
                product_id,
            ),
        )
    return get_product(product_id)


def list_products() -> List[Dict[str, str]]:
    with get_conn() as conn:
        rows = conn.execute('SELECT * FROM ops_products ORDER BY updated_at DESC').fetchall()
    return [dict(row) for row in rows]


def delete_product(product_id: str) -> None:
    with get_conn() as conn:
        conn.execute('DELETE FROM ops_products WHERE product_id = ?', (product_id,))


def upsert_grade(payload: GradeIn) -> Dict[str, str]:
    now = _now()
    with get_conn() as conn:
        conn.execute(
            '''
            INSERT INTO ops_grades (grade_id, label, criteria, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(grade_id) DO UPDATE SET
            label=excluded.label, criteria=excluded.criteria, updated_at=excluded.updated_at
            ''',
            (payload.gradeId, payload.label, payload.criteria, now, now)
        )
    return get_grade(payload.gradeId)


def get_grade(grade_id: str) -> Dict[str, str]:
    with get_conn() as conn:
        row = conn.execute('SELECT * FROM ops_grades WHERE grade_id = ?', (grade_id,)).fetchone()
    return _row_to_dict(row)


def list_grades() -> List[Dict[str, str]]:
    with get_conn() as conn:
        rows = conn.execute('SELECT * FROM ops_grades ORDER BY label').fetchall()
    return [dict(row) for row in rows]


def upsert_rule(payload: RuleIn) -> Dict[str, str]:
    now = _now()
    with get_conn() as conn:
        conn.execute(
            '''
            INSERT INTO ops_rules (rule_id, name, condition, action, active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(rule_id) DO UPDATE SET
            name=excluded.name,
            condition=excluded.condition,
            action=excluded.action,
            active=excluded.active,
            updated_at=excluded.updated_at
            ''',
            (
                payload.ruleId,
                payload.name,
                payload.condition,
                payload.action,
                1 if payload.active else 0,
                now,
                now,
            ),
        )
    return get_rule(payload.ruleId)


def get_rule(rule_id: str) -> Dict[str, str]:
    with get_conn() as conn:
        row = conn.execute('SELECT * FROM ops_rules WHERE rule_id = ?', (rule_id,)).fetchone()
    return _row_to_dict(row)


def list_rules() -> List[Dict[str, str]]:
    with get_conn() as conn:
        rows = conn.execute('SELECT * FROM ops_rules ORDER BY name').fetchall()
    return [dict(row) for row in rows]


def record_audit(entity_type: str, entity_id: str, action: str, actor: str, payload: Optional[str] = None) -> None:
    with get_conn() as conn:
        conn.execute(
            '''
            INSERT INTO ops_audit (entity_type, entity_id, action, actor, payload, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''',
            (entity_type, entity_id, action, actor, payload, _now())
        )


def list_audits(limit: int = 20) -> List[Dict[str, str]]:
    with get_conn() as conn:
        rows = conn.execute('SELECT * FROM ops_audit ORDER BY created_at DESC LIMIT ? ', (limit,)).fetchall()
    return [dict(row) for row in rows]
