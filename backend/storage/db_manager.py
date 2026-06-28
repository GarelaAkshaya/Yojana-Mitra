from __future__ import annotations

import sqlite3
from pathlib import Path

from backend.core.config import get_settings


class DatabaseManager:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or get_settings().paths.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def run_migrations(self) -> None:
        migrations_dir = Path(__file__).parent / "migrations"
        with self.connect() as conn:
            for migration in sorted(migrations_dir.glob("*.sql")):
                conn.executescript(migration.read_text(encoding="utf-8"))
