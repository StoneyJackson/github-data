# Dockerfile for kit-orchestrator package
# Convenience container bundling all GitHub data tools

FROM github-data-git-base:latest

# Install all subproject packages
COPY packages/git-repo-tools /tmp/git-repo-tools
COPY packages/github-repo-manager /tmp/github-repo-manager
COPY packages/github-data-tools /tmp/github-data-tools
COPY packages/kit-orchestrator /app

# Install dependencies in order
RUN cd /tmp/git-repo-tools && pdm install --prod && \
    cd /tmp/github-repo-manager && pdm install --prod && \
    cd /tmp/github-data-tools && pdm install --prod && \
    cd /app && pdm install --prod && \
    rm -rf /tmp/*

# Set entrypoint to orchestrator
ENTRYPOINT ["pdm", "run", "kit-orchestrator"]
