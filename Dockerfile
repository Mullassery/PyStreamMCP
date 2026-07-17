"""
Multi-stage Dockerfile for PyStreamMCP.

Build stages:
1. Builder: Compile Rust core + Python bindings
2. Runtime: Lean production image with API server
"""

FROM rust:1.81 AS builder

WORKDIR /app

# Install Python build dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    maturin \
    && rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . .

# Build Rust core and Python bindings
RUN cargo build --release --all-features
RUN maturin develop --release

# Stage 2: Runtime image
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Copy bindings from builder
COPY --from=builder /app/target/release /app/target/release
COPY --from=builder /app/python /app/python
COPY --from=builder /app/pyproject.toml /app/

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi>=0.104.0 \
    uvicorn[standard]>=0.24.0 \
    pydantic>=2.0 \
    pydantic-settings>=2.0

# Install PyStreamMCP
RUN pip install --no-cache-dir -e /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose API port
EXPOSE 8000

# Run API server
CMD ["python", "-m", "pystreammcp.api"]
