FROM python:3.12-slim

# Install system dependencies including Git
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install PDM
RUN pip install --no-cache-dir pdm

# Set working directory
WORKDIR /app

# Copy PDM files and README first for better caching
COPY pyproject.toml pdm.lock* README.md ./

# Install dependencies
RUN pdm install --prod --no-editable

# Copy source code
COPY github_data/ ./github_data/

# Create data directory for volume mounting
RUN mkdir -p /data

# Get the virtual environment path and configure environment
RUN pdm info --env > /tmp/venv_path
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Run the application using PDM
CMD ["pdm", "run", "python", "-m", "github_data.main"]
