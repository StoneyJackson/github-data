# Base Docker image for all GitHub data tools packages
# Provides Python environment, PDM, and core package

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

# Copy and install core package
COPY packages/core /tmp/core
RUN cd /tmp/core && pdm install --prod && rm -rf /tmp/core

# This is the base image that all subprojects extend
