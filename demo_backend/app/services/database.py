from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

from ..config import settings

DB_PATH = Path(settings.database_path)


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
        conn.commit()


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_user(email: str, full_name: str | None, password_hash: str) -> dict[str, Any]:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (email, full_name, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (email.lower(), full_name, password_hash, now),
        )
        conn.commit()
        cursor = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()
    return dict(row) if row else {}


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        cursor = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with get_conn() as conn:
        cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
    return dict(row) if row else None


def delete_session(token: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()


def create_session(user_id: int, token: str) -> None:
    expires_at = datetime.utcnow() + timedelta(minutes=settings.token_expiry_minutes)
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO sessions (token, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (token, user_id, expires_at.isoformat(), datetime.utcnow().isoformat()),
        )
        conn.commit()


def get_session(token: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        cursor = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,))
        row = cursor.fetchone()
    if not row:
        return None
    data = dict(row)
    if datetime.fromisoformat(data["expires_at"]) < datetime.utcnow():
        delete_session(token)
        return None
    return data


