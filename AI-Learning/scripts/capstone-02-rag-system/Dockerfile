# =============================================================================
# Dockerfile for RAG System
# =============================================================================
# Multi-stage build: dependencies first, then application code.
# Optimized for caching and minimal image size.
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Runtime
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local

COPY src/ ./src/
COPY streamlit_app.py .

# Create non-root user
RUN useradd --create-home appuser
USER appuser

# Expose FastAPI and Streamlit ports
EXPOSE 8000 8501

# Default: run the FastAPI server
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
