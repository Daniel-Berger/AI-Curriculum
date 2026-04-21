# =============================================================================
# Multi-stage Dockerfile for ML Pipeline
# =============================================================================
# Stage 1: Build dependencies in a builder image
# Stage 2: Copy only what's needed into a slim runtime image
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: Runtime
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ ./src/
COPY cli.py .

# Create non-root user
RUN useradd --create-home appuser
USER appuser

# Create directories for data and outputs
RUN mkdir -p data models reports

# Default entry point
ENTRYPOINT ["python", "cli.py"]
CMD ["run", "--help"]
