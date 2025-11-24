# Dockerfile for git-repo-tools package
# Tools for saving and restoring Git repositories

FROM github-data-git-base:latest

# Copy and install git-repo-tools package
COPY packages/git-repo-tools /app
RUN cd /app && pdm install --prod

# Set entrypoint
ENTRYPOINT ["pdm", "run", "git-repo-tools"]
