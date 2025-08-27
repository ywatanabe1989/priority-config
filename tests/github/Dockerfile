# Minimal Dockerfile for Local GitHub Actions Emulator  
FROM python:3.12

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Install git (minimal dependencies)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy project files
COPY pyproject.toml /workspace/
COPY src/ /workspace/src/
COPY tests/ /workspace/tests/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -e ".[dev]"

# Make scripts executable  
RUN chmod +x /workspace/tests/github/local_ci.py

ENTRYPOINT ["python", "/workspace/tests/github/local_ci.py"]