# Dockerfile for kit-orchestrator package
# Convenience container bundling all GitHub data tools

FROM github-data-git-base:latest

# All packages are already installed in base image
# This image just provides a specific entrypoint for kit-orchestrator

# Set entrypoint to orchestrator
ENTRYPOINT ["pdm", "run", "kit-orchestrator"]
