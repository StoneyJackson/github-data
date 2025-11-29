# Base Docker image for all GitHub data tools packages
# Provides Python environment, PDM, and all workspace packages

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PDM
RUN pip install --no-cache-dir pdm

# Set working directory
WORKDIR /app

# Copy root workspace files for dependency resolution
COPY pyproject.toml pdm.lock* README.md ./

# Copy all package sources (required for workspace dependencies)
COPY packages/ ./packages/

# Install all workspace packages in production mode
# Using --prod to skip dev dependencies
RUN pdm install --prod

# Create data directory for volume mounting
RUN mkdir -p /data

# Configure environment to find installed packages
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
# Add all package src directories to PYTHONPATH for monorepo
ENV PYTHONPATH=/app/packages/core/src:/app/packages/git-repo-tools/src:/app/packages/github-repo-manager/src:/app/packages/github-data-tools/src:/app/packages/kit-orchestrator/src:/app

# This is the base image that all subprojects extend
