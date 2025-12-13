# Multi-stage build for pipeline execution on Raspberry Pi (ARM64)
FROM python:3.11-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Final stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy uv and virtual environment from builder
COPY --from=builder /usr/local/bin/uv /usr/local/bin/uv
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY pipelines/ ./pipelines/
COPY Makefile ./
COPY pyproject.toml uv.lock ./

# Set Python path to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Default command (can be overridden)
CMD ["bash"]
