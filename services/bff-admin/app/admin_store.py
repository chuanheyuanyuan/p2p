from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from fastapi import HTTPException, status

from .config import AdminUser, Settings

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS admin_users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name TEXT,
    email TEXT,
    title TEXT,
    roles TEXT NOT NULL,
    permissions TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 120_000).hex()


def initialize_admin_store(settings: Settings) -> None:
    settings.admin_db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = _connect(settings.admin_db_path)
    try:
        conn.execute(CREATE_SQL)
        _seed_admin_users(conn, settings)
    finally:
        conn.close()


def _seed_admin_users(conn: sqlite3.Connection, settings: Settings) -> None:
    for entry in settings.admin_users:
        password_hash = _hash_password(entry.password, settings.admin_password_salt)
        conn.execute(
            """
            INSERT INTO admin_users (id, username, password_hash, display_name, email, title, roles, permissions, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                id=excluded.id,
                password_hash=excluded.password_hash,
                display_name=excluded.display_name,
                email=excluded.email,
                title=excluded.title,
                roles=excluded.roles,
                permissions=excluded.permissions,
                updated_at=excluded.updated_at
            """,
            (
                entry.id,
                entry.username,
                password_hash,
                entry.displayName,
                entry.email,
                entry.title,
                json.dumps(entry.roles, ensure_ascii=False),
                json.dumps(entry.permissions, ensure_ascii=False),
                datetime.utcnow().isoformat(),
            ),
        )
    conn.commit()


def _load_admin_row(settings: Settings, username: str) -> Tuple[Optional[sqlite3.Row], sqlite3.Connection]:
    conn = _connect(settings.admin_db_path)
    row = conn.execute('SELECT * FROM admin_users WHERE username = ?', (username,)).fetchone()
    return row, conn


def verify_admin_credentials(settings: Settings, username: str, password: str) -> AdminUser:
    row, conn = _load_admin_row(settings, username)
    try:
        if row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='账号或密码错误')
        candidate = _hash_password(password, settings.admin_password_salt)
        if candidate != row['password_hash']:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='账号或密码错误')
        return _row_to_admin_user(row)
    finally:
        conn.close()


def get_admin_user(settings: Settings, username: str) -> AdminUser:
    row, conn = _load_admin_row(settings, username)
    try:
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='管理员不存在')
        return _row_to_admin_user(row)
    finally:
        conn.close()


def _row_to_admin_user(row: sqlite3.Row) -> AdminUser:
    roles = json.loads(row['roles']) if row['roles'] else []
    permissions = json.loads(row['permissions']) if row['permissions'] else []
    return AdminUser(
        id=row['id'],
        username=row['username'],
        password=row['password_hash'],
        displayName=row['display_name'],
        email=row['email'],
        title=row['title'],
        roles=roles,
        permissions=permissions,
    )
