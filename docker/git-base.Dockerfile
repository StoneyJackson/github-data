# Git-enabled base Docker image for packages that need Git CLI
# Extends base.Dockerfile with Git installation

FROM github-data-base:latest AS git-base

# Install Git
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Configure Git (minimal config for operations)
RUN git config --global user.email "github-data@example.com" && \
    git config --global user.name "GitHub Data Tools"

# This base is used by git-repo-tools and kit-orchestrator
