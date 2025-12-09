# Simple Dockerfile for Railway deployment
# Root directory should be set to "backend" in Railway settings

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8000

# Run with PORT from environment variable (Railway sets this)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
