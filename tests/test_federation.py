"""Federated execution tests use local SQLite/CSV sources; no servers."""

from __future__ import annotations

import sqlite3

import pytest

pytest.importorskip("duckdb")
pytest.importorskip("sqlglot")

from pystreammcp.federation import FederatedQueryEngine, execute_federated


def _sqlite(path, rows):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT)")
    conn.executemany("INSERT INTO customers VALUES (?, ?)", rows)
    conn.commit()
    conn.close()


def test_join_two_sqlite_sources(tmp_path):
    _sqlite(tmp_path / "a.db", [(1, "Ada"), (2, "Grace")])
    _sqlite(tmp_path / "b.db", [(1, "ada@example.com"), (2, "grace@example.com")])
    with FederatedQueryEngine() as engine:
        engine.register_sqlite("a", tmp_path / "a.db")
        engine.register_sqlite("b", tmp_path / "b.db")
        result = engine.execute_join(
            "a.customers",
            "b.customers",
            "l.id = r.id",
            columns="l.id, l.name, r.name AS email",
        )
    assert result.columns == ["id", "name", "email"]
    assert len(result.rows) == 2
    assert result.rows[0][1] == "Ada"


def test_execute_federated_sqlite_and_limit(tmp_path):
    _sqlite(tmp_path / "a.db", [(1, "Ada"), (2, "Grace")])
    result = execute_federated(
        "SELECT * FROM a.customers ORDER BY id",
        {"a": f"sqlite:{tmp_path / 'a.db'}"},
        limit=1,
    )
    assert len(result.rows) == 1
    assert result.truncated


def test_rejects_bad_alias():
    with pytest.raises(ValueError, match="invalid source alias"):
        FederatedQueryEngine().register_sqlite("bad; drop", "x")


def test_handler_uses_engine_when_configured(tmp_path):
    import asyncio

    from pystreammcp._mcp_tools import PyStreamMCPHandler

    _sqlite(tmp_path / "a.db", [(1, "Ada")])
    _sqlite(tmp_path / "b.db", [(1, "ada@example.com")])
    engine = FederatedQueryEngine()
    engine.register_sqlite("a", tmp_path / "a.db")
    engine.register_sqlite("b", tmp_path / "b.db")

    class _Orchestrator:
        def handle_cross_database_join(self, *args):
            raise AssertionError("fallback should not run")

    handler = PyStreamMCPHandler(_Orchestrator(), federation_engine=engine)
    result = asyncio.run(
        handler.handle_cross_database_join("a.customers", "b.customers", "l.id = r.id")
    )
    assert result["status"] == "ok"
    assert result["rows"] == [[1, "Ada", 1, "ada@example.com"]]
