"""SQLite helpers for server inventory and latest metrics."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, current_app, g


def _default_db_path(app: Flask) -> Path:
    configured = app.config.get("DATABASE_PATH") or ""
    if configured:
        return Path(configured)
    return Path(app.instance_path) / "monitoring.db"


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        path = _default_db_path(current_app)
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(_: Any = None) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db(app: Flask) -> None:
    with app.app_context():
        db = get_db()
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS servers (
                id TEXT PRIMARY KEY,
                hostname TEXT NOT NULL,
                ssh_username TEXT NOT NULL,
                ssh_port INTEGER NOT NULL DEFAULT 22,
                labels TEXT NOT NULL DEFAULT '',
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS metrics (
                server_id TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL,
                received_at TEXT NOT NULL,
                FOREIGN KEY (server_id) REFERENCES servers(id)
            );
            """
        )
        db.commit()


def list_servers(*, enabled_only: bool = False) -> list[dict[str, Any]]:
    db = get_db()
    if enabled_only:
        rows = db.execute(
            "SELECT * FROM servers WHERE enabled = 1 ORDER BY created_at DESC"
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM servers ORDER BY created_at DESC").fetchall()
    return [dict(row) for row in rows]


def get_server(server_id: str) -> dict[str, Any] | None:
    row = get_db().execute("SELECT * FROM servers WHERE id = ?", (server_id,)).fetchone()
    return dict(row) if row else None


def find_enabled_server_by_hostname(hostname: str) -> dict[str, Any] | None:
    row = get_db().execute(
        "SELECT * FROM servers WHERE hostname = ? AND enabled = 1",
        (hostname,),
    ).fetchone()
    return dict(row) if row else None


def add_server(
    hostname: str,
    ssh_username: str,
    ssh_port: int,
    labels: str = "",
) -> dict[str, Any]:
    server_id = uuid.uuid4().hex[:12]
    created_at = datetime.now(timezone.utc).isoformat()
    get_db().execute(
        """
        INSERT INTO servers (id, hostname, ssh_username, ssh_port, labels, enabled, created_at)
        VALUES (?, ?, ?, ?, ?, 1, ?)
        """,
        (server_id, hostname, ssh_username, ssh_port, labels, created_at),
    )
    get_db().commit()
    return get_server(server_id)  # type: ignore[return-value]


def set_server_enabled(server_id: str, enabled: bool) -> dict[str, Any] | None:
    result = get_db().execute(
        "UPDATE servers SET enabled = ? WHERE id = ?",
        (1 if enabled else 0, server_id),
    )
    get_db().commit()
    if result.rowcount == 0:
        return None
    return get_server(server_id)


def store_metrics(server_id: str, payload: dict[str, Any]) -> None:
    received_at = datetime.now(timezone.utc).isoformat()
    get_db().execute(
        """
        INSERT INTO metrics (server_id, payload_json, received_at)
        VALUES (?, ?, ?)
        ON CONFLICT(server_id) DO UPDATE SET
            payload_json = excluded.payload_json,
            received_at = excluded.received_at
        """,
        (server_id, json.dumps(payload), received_at),
    )
    get_db().commit()


def get_metrics(server_id: str) -> dict[str, Any] | None:
    row = get_db().execute(
        "SELECT payload_json, received_at FROM metrics WHERE server_id = ?",
        (server_id,),
    ).fetchone()
    if not row:
        return None
    payload = json.loads(row["payload_json"])
    payload["received_at"] = row["received_at"]
    return payload
