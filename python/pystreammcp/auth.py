"""HTTP authentication for PyStreamMCP servers.

When ``PYSTREAMMCP_API_KEY`` is set, every non-health route requires
``X-API-Key`` or ``Authorization: Bearer``. When it is not set, only loopback
clients are accepted, so a network-exposed server fails closed instead of
serving query/source data anonymously.
"""

from __future__ import annotations

import hmac
import os

API_KEY_ENV = "PYSTREAMMCP_API_KEY"


def _loopback(host: str | None) -> bool:
    if not host:
        return False
    return host in {"127.0.0.1", "::1", "localhost", "testclient"} or host.startswith(
        "127."
    )


def check_request(
    remote_addr: str | None,
    x_api_key: str | None,
    authorization: str | None,
) -> tuple[bool, str]:
    expected = os.environ.get(API_KEY_ENV)
    if expected:
        supplied = x_api_key
        if (
            not supplied
            and authorization
            and authorization.lower().startswith("bearer ")
        ):
            supplied = authorization[7:].strip()
        if not supplied or not hmac.compare_digest(supplied, expected):
            return False, "invalid or missing API key"
        return True, ""
    if not _loopback(remote_addr):
        return (
            False,
            f"refusing non-loopback request without authentication; set {API_KEY_ENV}",
        )
    return True, ""


def install_flask_auth(app) -> None:
    """Install a before_request guard on a Flask app."""
    from flask import jsonify, request

    @app.before_request
    def _auth_guard():  # pragma: no cover - exercised via app test client
        if request.path == "/health":
            return None
        ok, message = check_request(
            request.remote_addr,
            request.headers.get("X-API-Key"),
            request.headers.get("Authorization"),
        )
        if not ok:
            return jsonify({"error": message}), (
                401 if os.environ.get(API_KEY_ENV) else 403
            )
        return None


__all__ = ["API_KEY_ENV", "check_request", "install_flask_auth"]
