"""Optional federated query execution with DuckDB + SQLGlot.

DuckDB (MIT) can attach SQLite/PostgreSQL/MySQL sources and read CSV/Parquet
locally; SQLGlot (MIT) transpiles dialect-specific SQL. This module gives
PyStreamMCP a real read-only execution backend instead of returning
``not_implemented`` for cross-source work.

Install::

    pip install "pystreammcp[federation]"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class FederationUnavailable(RuntimeError):
    """Raised when duckdb/sqlglot are not installed."""


@dataclass
class FederatedResult:
    columns: list[str]
    rows: list[list[Any]]
    sources: dict[str, str] = field(default_factory=dict)
    truncated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "columns": self.columns,
            "rows": self.rows,
            "sources": self.sources,
            "truncated": self.truncated,
        }


def _require_deps():
    try:
        import duckdb
    except ImportError as exc:
        raise FederationUnavailable(
            "duckdb is required for federation. Install with "
            '`pip install "pystreammcp[federation]"`.'
        ) from exc
    try:
        import sqlglot
    except ImportError as exc:
        raise FederationUnavailable(
            "sqlglot is required for federation. Install with "
            '`pip install "pystreammcp[federation]"`.'
        ) from exc
    return duckdb, sqlglot


def _quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _quote_table(name: str) -> str:
    parts = [part for part in name.split(".") if part]
    if not parts:
        raise ValueError("empty table name")
    return ".".join(_quote_ident(part) for part in parts)


def _safe_alias(alias: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", alias):
        raise ValueError(f"invalid source alias: {alias!r}")
    return alias


class FederatedQueryEngine:
    """Read-only DuckDB connection over registered sources."""

    def __init__(self):
        duckdb, _ = _require_deps()
        self._duckdb = duckdb
        self._conn = duckdb.connect(database=":memory:")
        self.sources: dict[str, str] = {}

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> FederatedQueryEngine:  # noqa: PYI034
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def register_sqlite(self, alias: str, path: str | Path) -> None:
        alias = _safe_alias(alias)
        escaped = str(path).replace("'", "''")
        self._conn.execute(
            f"ATTACH '{escaped}' AS {_quote_ident(alias)} (TYPE sqlite, READ_ONLY)"
        )
        self.sources[alias] = f"sqlite:{path}"

    def register_parquet(self, alias: str, path: str | Path) -> None:
        alias = _safe_alias(alias)
        self._conn.execute(
            f"CREATE OR REPLACE VIEW {_quote_ident(alias)} AS SELECT * FROM read_parquet(?)",
            [str(path)],
        )
        self.sources[alias] = f"parquet:{path}"

    def register_csv(self, alias: str, path: str | Path) -> None:
        alias = _safe_alias(alias)
        self._conn.execute(
            f"CREATE OR REPLACE VIEW {_quote_ident(alias)} AS SELECT * FROM read_csv_auto(?)",
            [str(path)],
        )
        self.sources[alias] = f"csv:{path}"

    def execute(
        self,
        query: str,
        *,
        dialect: str = "duckdb",
        limit: int = 1000,
    ) -> FederatedResult:
        _, sqlglot = _require_deps()
        if limit <= 0:
            raise ValueError("limit must be positive")
        if dialect != "duckdb":
            query = sqlglot.transpile(query, read=dialect, write="duckdb")[0]
        wrapped = f"SELECT * FROM ({query}) AS _federated LIMIT {int(limit) + 1}"
        cursor = self._conn.execute(wrapped)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description or []]
        truncated = len(rows) > limit
        if truncated:
            rows = rows[:limit]
        return FederatedResult(
            columns=columns,
            rows=[list(row) for row in rows],
            sources=dict(self.sources),
            truncated=truncated,
        )

    def execute_join(
        self,
        left_source: str,
        right_source: str,
        join_key: str,
        *,
        join_type: str = "inner",
        columns: str = "*",
        limit: int = 1000,
    ) -> FederatedResult:
        join_type = join_type.lower()
        if join_type not in {"inner", "left", "right", "full"}:
            raise ValueError("join_type must be inner/left/right/full")
        # The sources are aliases/tables; join_key is an SQL expression the
        # caller controls, but this engine is read-only and bounded.
        query = (
            f"SELECT {columns} FROM {_quote_table(left_source)} AS l "
            f"{join_type.upper()} JOIN {_quote_table(right_source)} AS r "
            f"ON {join_key}"
        )
        return self.execute(query, limit=limit)


def execute_federated(
    query: str,
    sources: dict[str, str],
    *,
    dialect: str = "duckdb",
    limit: int = 1000,
) -> FederatedResult:
    """Convenience: register ``alias -> uri`` sources and run ``query``.

    URI forms: ``sqlite:/path/db``, ``parquet:/path/file``, ``csv:/path/file``.
    """
    with FederatedQueryEngine() as engine:
        for alias, uri in sources.items():
            scheme, _, path = uri.partition(":")
            if scheme == "sqlite":
                engine.register_sqlite(alias, path)
            elif scheme == "parquet":
                engine.register_parquet(alias, path)
            elif scheme == "csv":
                engine.register_csv(alias, path)
            else:
                raise ValueError(f"unsupported source scheme: {scheme}")
        return engine.execute(query, dialect=dialect, limit=limit)


__all__ = [
    "FederatedQueryEngine",
    "FederatedResult",
    "FederationUnavailable",
    "execute_federated",
]
