# Kit Orchestrator - Complete GitHub data operations package
# Combines all subprojects for full freeze/restore workflows

# Builder stage
FROM python:3.11-slim AS builder

# Install PDM
RUN pip install --no-cache-dir pdm

WORKDIR /build

# Copy workspace configuration
COPY pyproject.toml pdm.lock ./

# Copy all package sources
COPY packages/core ./packages/core
COPY packages/git-repo-tools ./packages/git-repo-tools
COPY packages/github-repo-manager ./packages/github-repo-manager
COPY packages/github-data-tools ./packages/github-data-tools
COPY packages/kit-orchestrator ./packages/kit-orchestrator

# Install all dependencies (including all packages)
RUN pdm install --prod --no-editable

# Runtime stage
FROM python:3.11-slim

# Install git (required for git operations)
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /build/.venv /app/.venv

# Set up environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/.venv/lib/python3.11/site-packages"

# Entry point
ENTRYPOINT ["python", "-m", "kit_orchestrator"]
