# syntax=docker/dockerfile:1.7
# Use official Python runtime as base image
FROM python:3.14-slim-trixie

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy pyproject.toml and setup files first for better layer caching
COPY pyproject.toml .

# Install build dependencies with trusted hosts to avoid SSL issues
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    setuptools>=80.0

# Copy application code
COPY . .

RUN pip install .

# Create non-root user for security
RUN useradd -m -u 1000 celeryuser && \
    chown -R celeryuser:celeryuser /app

# Switch to non-root user
USER celeryuser

# Default command to run Celery worker
CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info", "-Q", "notifications"]
