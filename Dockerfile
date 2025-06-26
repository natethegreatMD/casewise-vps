# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies (minimal for development)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY casewise/ ./casewise/
COPY pyproject.toml .

# Create necessary directories
RUN mkdir -p logs output rubrics cases source-documents demo_cases

# Create non-root user
RUN useradd --create-home --shell /bin/bash casewise && \
    chown -R casewise:casewise /app

# Switch to non-root user
USER casewise

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f https://api.casewisemd.org/health || exit 1

# Default command
CMD ["uvicorn", "casewise.main:app", "--host", "0.0.0.0", "--port", "8000"] 