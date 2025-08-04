# Minimal Docker image for Railway - target <2GB
FROM python:3.11-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/*

# Install only core dependencies - remove heaviest ML packages
RUN pip install --no-cache-dir \
    fastapi==0.116.1 \
    uvicorn==0.35.0 \
    pandas==2.3.1 \
    numpy==2.3.2 \
    boto3==1.34.162 \
    python-dotenv==1.0.1 \
    pydantic==2.11.7 \
    requests==2.32.4 \
    && pip cache purge \
    && rm -rf /root/.cache/pip

# Copy only essential source files (data excluded via .dockerignore)
COPY src/r2_config.py ./src/
COPY minimal_api.py ./

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Use the minimal API
CMD ["python", "minimal_api.py"]
