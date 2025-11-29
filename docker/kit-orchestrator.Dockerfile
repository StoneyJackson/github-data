# Kit Orchestrator - Complete GitHub data operations package
# Combines all subprojects for full freeze/restore workflows

# Builder stage
FROM python:3.11-slim AS builder

# Install PDM
RUN pip install --no-cache-dir pdm

WORKDIR /build

# Copy workspace configuration
COPY pyproject.toml pdm.lock README.md ./

# Copy all package sources
COPY packages/core ./packages/core
COPY packages/git-repo-tools ./packages/git-repo-tools
COPY packages/github-repo-manager ./packages/github-repo-manager
COPY packages/github-data-tools ./packages/github-data-tools
COPY packages/kit-orchestrator ./packages/kit-orchestrator

# Create README.md files for packages that reference them in pyproject.toml
RUN for pkg in packages/core packages/git-repo-tools packages/github-repo-manager packages/github-data-tools; do \
        if [ ! -f "$pkg/README.md" ]; then cp README.md "$pkg/README.md"; fi; \
    done

# Install dependencies first (without workspace packages)
RUN pdm export --prod -o requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Build and install each package in dependency order
RUN cd packages/core && pip install --no-cache-dir . && \
    cd ../git-repo-tools && pip install --no-cache-dir . && \
    cd ../github-repo-manager && pip install --no-cache-dir . && \
    cd ../github-data-tools && pip install --no-cache-dir . && \
    cd ../kit-orchestrator && pip install --no-cache-dir .

# Runtime stage
FROM python:3.11-slim

# Install git (required for git operations)
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package sources (needed for entity configs and data files)
COPY --from=builder /build/packages /app/packages

# Copy installed packages from builder's Python site-packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Entry point
ENTRYPOINT ["python", "-m", "kit_orchestrator"]
