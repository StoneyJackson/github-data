# Dockerfile for github-data-tools package
# Tools for saving and restoring GitHub repository data

FROM github-data-base:latest

# All packages are already installed in base image
# This image just provides a specific entrypoint for github-data-tools

# Set entrypoint
ENTRYPOINT ["pdm", "run", "github-data-tools"]
