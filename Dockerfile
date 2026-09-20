# Dockerfile for PyStreamMCP.
#
# The published package is pure Python (setuptools build, see
# pyproject.toml) — no Rust toolchain or compiler is required or used.
# The `core`/`python` Rust workspace at the repo root is a separate,
# currently-non-compiling, unshipped experiment (see README's
# "Rust workspace (not shipped)" section) and is intentionally NOT built
# here.
#
# NOTE: `python -m pystreammcp.api` only defines the FastAPI app; it has
# no `if __name__ == "__main__"` entry point, so the CMD below invokes
# uvicorn directly against the app factory instead of relying on one.
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml setup.py MANIFEST.in README.md LICENSE ./
COPY python ./python

RUN pip install --no-cache-dir ".[api]"

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

CMD ["uvicorn", "pystreammcp.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
