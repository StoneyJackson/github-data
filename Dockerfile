FROM python:3.11-slim

# Install PDM
RUN pip install --no-cache-dir pdm

# Set working directory
WORKDIR /app

# Copy PDM files and README first for better caching
COPY pyproject.toml pdm.lock* README.md ./

# Install dependencies
RUN pdm install --prod --no-editable

# Copy source code
COPY src/ ./src/

# Create data directory for volume mounting
RUN mkdir -p /data

# Set environment variables
ENV PYTHONPATH=/app
ENV DATA_PATH=/data

# Run the application using PDM
CMD ["pdm", "run", "python", "-m", "src.main"]