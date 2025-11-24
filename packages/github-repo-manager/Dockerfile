# Dockerfile for github-repo-manager package
# GitHub repository lifecycle management tools

FROM github-data-base:latest

# Copy and install github-repo-manager package
COPY packages/github-repo-manager /app
RUN cd /app && pdm install --prod

# Set entrypoint
ENTRYPOINT ["pdm", "run", "github-repo-manager"]
