# --- Stage 1: Builder ---
FROM python:3.13-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# --- Stage 2: Runtime ---
FROM python:3.13-slim-bookworm

WORKDIR /app

# Copy uv and the venv from builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=builder /app/backend/.venv /app/backend/.venv

ENV PATH="/app/backend/.venv/bin:$PATH" \
    PYTHONPATH=/app

# Copy backend source as a package under /app/backend
COPY . ./backend/

# sample-documents lives at /app/sample-documents (matches config.py: parent.parent / "sample-documents")
# Mount or copy them at runtime via docker-compose volume

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
