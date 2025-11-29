# Dockerfile for git-repo-tools package
# Tools for saving and restoring Git repositories

FROM github-data-git-base:latest

# All packages are already installed in base image
# This image just provides a specific entrypoint for git-repo-tools

# Set entrypoint
ENTRYPOINT ["pdm", "run", "git-repo-tools"]
