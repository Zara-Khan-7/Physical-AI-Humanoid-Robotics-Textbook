# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (copy from backend folder since context is repo root)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code from backend folder
COPY --chown=appuser:appuser backend/app ./app
COPY --chown=appuser:appuser backend/requirements.txt .

# Switch to non-root user
USER appuser

# Expose port (Railway sets PORT env var)
EXPOSE 8000

# Run with PORT from environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
