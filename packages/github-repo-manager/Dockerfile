# Dockerfile for github-repo-manager package
# GitHub repository lifecycle management tools

FROM github-data-base:latest

# All packages are already installed in base image
# This image just provides a specific entrypoint for github-repo-manager

# Set entrypoint
ENTRYPOINT ["pdm", "run", "github-repo-manager"]
