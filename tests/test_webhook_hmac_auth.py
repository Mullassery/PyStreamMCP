"""Tests proving the orchestration webhook HTTP endpoint enforces real
HMAC-SHA256 authentication.

Before this fix, POST /orchestration/webhooks/events (server.py's Flask
app) accepted any JSON body from anyone with zero authentication, despite
the README advertising "Production-Grade Webhooks ... (HMAC-SHA256
security)". The one existing "HMAC" test in the repo
(test_integration_phase2.py::test_webhook_signature_validation) only
recomputed hmac.new() twice locally and compared them — it never touched
the actual server code at all, so it proved nothing about real endpoint
behavior.

These tests exercise the real Flask app via its test client:
  - No signature header -> rejected
  - Wrong/tampered signature -> rejected
  - No secret configured at all -> rejected (fails closed, not open)
  - Correct signature -> accepted and the event is actually processed
"""

import hashlib
import hmac as hmac_module
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

import pytest

flask = pytest.importorskip("flask", reason="Flask is required for the webhook HTTP server")

from pystreammcp.server import (
    PyStreamMCPServer,
    create_flask_app,
    compute_webhook_signature,
    verify_webhook_signature,
    WEBHOOK_SIGNATURE_HEADER,
)


SECRET = "test-shared-secret"


def _client(secret=SECRET):
    app = create_flask_app(server=PyStreamMCPServer(), webhook_secret=secret)
    app.config["TESTING"] = True
    return app.test_client()


def _event_payload():
    return {
        "event_type": "mcp.available",
        "data": {"project_name": "demo", "mcp_port": 9100, "tools": []},
    }


class TestSignatureHelpers:
    def test_compute_and_verify_round_trip(self):
        payload = b'{"event_type": "mcp.available"}'
        sig = compute_webhook_signature(SECRET, payload)
        is_valid, error = verify_webhook_signature(SECRET, payload, sig)
        assert is_valid
        assert error == ""

    def test_tampered_payload_fails_verification(self):
        payload = b'{"event_type": "mcp.available"}'
        sig = compute_webhook_signature(SECRET, payload)
        tampered_payload = b'{"event_type": "malicious.event"}'
        is_valid, error = verify_webhook_signature(SECRET, tampered_payload, sig)
        assert not is_valid
        assert "Invalid" in error

    def test_missing_secret_fails_closed(self):
        payload = b"{}"
        sig = compute_webhook_signature(SECRET, payload)
        is_valid, error = verify_webhook_signature(None, payload, sig)
        assert not is_valid
        assert "no shared secret" in error


class TestWebhookEndpointRejectsUnauthenticated:
    def test_no_signature_header_is_rejected(self):
        client = _client()
        response = client.post(
            "/orchestration/webhooks/events",
            data=json.dumps(_event_payload()),
            content_type="application/json",
        )
        assert response.status_code == 401
        assert response.get_json()["status"] == "error"

    def test_wrong_secret_signature_is_rejected(self):
        client = _client()
        body = json.dumps(_event_payload()).encode()
        wrong_sig = compute_webhook_signature("not-the-real-secret", body)
        response = client.post(
            "/orchestration/webhooks/events",
            data=body,
            content_type="application/json",
            headers={WEBHOOK_SIGNATURE_HEADER: wrong_sig},
        )
        assert response.status_code == 401

    def test_tampered_body_after_signing_is_rejected(self):
        """Signature computed over one body, but a different body is sent —
        simulates a man-in-the-middle payload tamper."""
        client = _client()
        original_body = json.dumps(_event_payload()).encode()
        sig = compute_webhook_signature(SECRET, original_body)
        tampered_body = json.dumps({**_event_payload(), "event_type": "evil"}).encode()

        response = client.post(
            "/orchestration/webhooks/events",
            data=tampered_body,
            content_type="application/json",
            headers={WEBHOOK_SIGNATURE_HEADER: sig},
        )
        assert response.status_code == 401

    def test_no_secret_configured_rejects_everything(self):
        """Fails closed: with no shared secret configured at all, even a
        request with no signature header gets a clear 503, and the event
        handler is never reached — there is no silent "allow unsigned"
        fallback."""
        client = _client(secret=None)
        response = client.post(
            "/orchestration/webhooks/events",
            data=json.dumps(_event_payload()),
            content_type="application/json",
        )
        assert response.status_code == 503


class TestWebhookEndpointAcceptsAuthenticated:
    def test_correctly_signed_request_is_accepted_and_processed(self):
        client = _client()
        body = json.dumps(_event_payload()).encode()
        sig = compute_webhook_signature(SECRET, body)

        response = client.post(
            "/orchestration/webhooks/events",
            data=body,
            content_type="application/json",
            headers={WEBHOOK_SIGNATURE_HEADER: sig},
        )

        assert response.status_code == 200
        result = response.get_json()
        assert result["status"] == "success"
        # The event was actually routed/dispatched, not just accepted and
        # discarded: the handler result confirms the project got registered.
        assert result["handler_result"]["project_name"] == "demo"

    def test_env_var_secret_is_picked_up_when_not_passed_explicitly(self, monkeypatch):
        monkeypatch.setenv("PYSTREAMMCP_WEBHOOK_SECRET", SECRET)
        app = create_flask_app(server=PyStreamMCPServer())  # no explicit secret
        app.config["TESTING"] = True
        client = app.test_client()

        body = json.dumps(_event_payload()).encode()
        sig = compute_webhook_signature(SECRET, body)
        response = client.post(
            "/orchestration/webhooks/events",
            data=body,
            content_type="application/json",
            headers={WEBHOOK_SIGNATURE_HEADER: sig},
        )
        assert response.status_code == 200
