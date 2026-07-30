# PyStreamMCP

Two-stage selective intelligence: metadata-first filtering + contextual reranking. 90-95% token reduction. OpenAI-compatible MCP orchestration layer for streaming.

**Latest Version:** 1.1.2 | **Python:** 3.9-3.13 | **License:** Proprietary | **Status:** ✅ Production Ready

### v1.1.2 Updates
- 🐍 Python 3.13 support certified
- 🔒 License updated to Proprietary
- ✅ Full dependency compatibility on Python 3.9-3.13

## Features

- ✅ 90-95% token reduction (selective intelligence)
- ✅ 8+ connected tools with latency tracking
- ✅ Metadata-first filtering & contextual reranking
- ✅ Production-ready CLI dashboards
- ✅ Keyboard shortcuts for quick access
- ✅ OpenTelemetry support (6 backends)

## Installation

```bash
pip install pystreammcp
```

## Quick Start

```bash
# Setup shortcuts
bash scripts/setup_shortcuts.sh

# View dashboard
dash-pystreammcp              # Static snapshot
dash-pystreammcp-live         # Live monitoring
dash-pystreammcp-export       # Export metrics

# Connect tools
pystreammcp list-tools
pystreammcp connect --provider openai
```

## Dashboard

Real-time MCP orchestration metrics:
- `dash-pystreammcp` - View tool status, selective intelligence stats
- `dash-pystreammcp-live` - Watch active executions, routing performance
- `dash-pystreammcp-export` - Export to JSON

**Metrics:** Status, Connected Tools (8+), Selective Intelligence Reduction (90-95%), Active Jobs, Routing Performance

## OpenTelemetry

Export to Prometheus, Datadog, Honeycomb, New Relic, Jaeger, or X-Ray.

```bash
export OTEL_EXPORTER_OTLP_PROTOCOL=prometheus
dash-pystreammcp-live
```

See `OTEL_SETUP_GUIDE.md`.

## Production Deployment

Kubernetes, Docker Compose, and standalone patterns included.

See `PRODUCTION_DEPLOYMENT.md`.

## Documentation

- `DASHBOARD_SHORTCUTS.md` - Keyboard shortcuts
- `OTEL_SETUP_GUIDE.md` - OpenTelemetry setup
- `PRODUCTION_DEPLOYMENT.md` - Deployment patterns

## Repository

- GitHub: https://github.com/Mullassery/PyStreamMCP
- PyPI: https://pypi.org/project/pystreammcp

## License

MIT
