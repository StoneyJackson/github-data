FROM python:3.12-slim

# Install system dependencies including Git
RUN apt-get update && apt-get install -y \
    git \
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
# Note: Using --prod to skip dev dependencies, but not --no-editable
# because workspace members need to be findable by Python
RUN pdm install --prod

# Create data directory for volume mounting
RUN mkdir -p /data

# Get the virtual environment path and configure environment
RUN pdm info --env > /tmp/venv_path
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
# Add all package src directories to PYTHONPATH for monorepo
ENV PYTHONPATH=/app/packages/core/src:/app/packages/git-repo-tools/src:/app/packages/github-repo-manager/src:/app/packages/github-data-tools/src:/app/packages/kit-orchestrator/src:/app

# Run the kit-orchestrator application using PDM
CMD ["pdm", "run", "python", "-m", "kit_orchestrator"]
