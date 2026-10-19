"""Live cross-repo test: PyStreamMCP quality gates -> StatGuardian /validate.

Starts a real ``statguardian serve`` process and exercises the validator's
service mode. Skipped when the StatGuardian CLI is absent; a skip is not
evidence of support.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
from pathlib import Path

import pytest

from pystreammcp.quality import QualityStatus, QualityValidator, ValidationGate


def _find_statguardian() -> str | None:
    explicit = os.environ.get("STATGUARDIAN_BIN")
    if explicit and Path(explicit).is_file():
        return explicit
    projects = Path(__file__).resolve().parents[2]
    for candidate in (
        projects / "statguardian" / ".venv" / "bin" / "statguardian",
        projects / "StatGuardian" / ".venv" / "bin" / "statguardian",
    ):
        if candidate.is_file():
            return str(candidate)
    return shutil.which("statguardian")


STATGUARDIAN = _find_statguardian()

pytestmark = pytest.mark.skipif(
    STATGUARDIAN is None,
    reason="statguardian CLI not found (set STATGUARDIAN_BIN or install statguardian[api])",
)

CONTRACT = """dataset tiny {
    schema {
        id:   int,    not_null
        name: string, not_null
    }
}
"""


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait(port: int, timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.1)
    raise AssertionError(f"StatGuardian did not listen on {port}")


def _validator(url: str) -> QualityValidator:
    validator = QualityValidator(statguardian_url=url)
    for dataset_id in ("good", "bad", "down"):
        validator.register_gate(ValidationGate(dataset_id=dataset_id, min_quality_score=0.7))
    return validator


def test_quality_gate_against_live_statguardian(tmp_path: Path) -> None:
    contract = tmp_path / "tiny.sg"
    contract.write_text(CONTRACT, encoding="utf-8")
    port = _free_port()
    process = subprocess.Popen(
        [
            STATGUARDIAN,
            "serve",
            "--contract",
            str(contract),
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait(port)
        validator = _validator(f"http://127.0.0.1:{port}")

        good = validator.validate("good", {"id": 1, "name": "x"})
        assert good.status == QualityStatus.VALID, good.errors

        bad = validator.validate("bad", {"id": None, "name": "x"})
        assert bad.status in (QualityStatus.INVALID, QualityStatus.DEGRADED)
        assert bad.errors

        down = _validator("http://127.0.0.1:9").validate("down", {"id": 1, "name": "x"})
        assert down.status == QualityStatus.UNKNOWN
        assert down.errors
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
