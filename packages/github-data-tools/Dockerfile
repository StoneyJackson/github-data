# Dockerfile for github-data-tools package
# Tools for saving and restoring GitHub repository data

FROM github-data-base:latest

# Copy and install github-data-tools package
COPY packages/github-data-tools /app
RUN cd /app && pdm install --prod

# Set entrypoint
ENTRYPOINT ["pdm", "run", "github-data-tools"]
