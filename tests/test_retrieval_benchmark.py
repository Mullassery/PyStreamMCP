import json
import subprocess
import sys


def run(*args):
    return subprocess.run(
        [sys.executable, "benchmarks/retrieval_bench.py", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_fake_benchmark_offline():
    r = run("--queries", "2", "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["mode"] == "fake"
    assert data["sample_count"] == 2
    assert data["error_count"] == 0
    assert data["p50_ms"] >= 0 and data["p95_ms"] >= data["p50_ms"]


def test_rejects_negative_queries():
    assert run("--queries", "-1", "--json").returncode != 0
