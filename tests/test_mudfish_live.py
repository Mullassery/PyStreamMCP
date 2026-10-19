"""Real cross-repo test: PyStreamMCP crawl tool -> MudFish engine.

This invokes the actual MudFish binary/binding through the MCP tool. Loopback
URLs are skipped by MudFish's SSRF guard, so the test verifies the real engine
run and result shaping without an external network. A successful external fetch
is **not tested** here (non-deterministic/network-dependent).
"""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

pytest.importorskip("mudfish")

from pystreammcp.mcp_server import PyStreamMCPServer


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler API
        body = b"<html><head><title>local</title></head></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):  # keep the test output quiet
        pass


def test_crawl_tool_runs_real_mudfish_and_applies_ssrf_guard() -> None:
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = PyStreamMCPServer().call_tool(
            "pystreammcp_crawl", {"url": f"http://127.0.0.1:{port}"}
        )
    finally:
        server.shutdown()
        thread.join(timeout=5)

    assert result["status"] == "success"
    assert result["pages"] == [], "loopback must be skipped by the SSRF guard"
    assert result["stats"]["urls_discovered"] == 1
    assert result["stats"]["urls_skipped"] == 1
    assert result["stats"]["urls_fetched"] == 0
