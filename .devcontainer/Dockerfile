# Use the official Microsoft DevContainer base image with Docker-in-Docker
FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI and Docker Compose
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (needed for Claude Code)
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs

# Install Python (useful for development)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code
RUN npm install -g @anthropic-ai/claude-code

# Create docker group and add vscode user to it
# (vscode user is created by the base image)
RUN groupadd -f docker && usermod -aG docker vscode

# Set up workspace directory
WORKDIR /workspace

# Switch to vscode user
USER vscode

# Set up shell aliases and environment for vscode user
RUN echo 'export PATH="$(npm bin -g):$PATH"' >> ~/.bashrc

# Switch back to root for any final setup
USER root

# Ensure proper permissions
RUN chown -R vscode:vscode /workspace

# Final switch to vscode user
USER vscode

# Default command
CMD ["/bin/bash"]
