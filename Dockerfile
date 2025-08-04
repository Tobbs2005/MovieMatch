# Multi-stage build to reduce final image size while keeping AI
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages to a local directory
RUN pip install --user --no-cache-dir \
    fastapi==0.116.1 \
    uvicorn==0.35.0 \
    pandas==2.3.1 \
    numpy==2.3.2 \
    sentence-transformers==5.0.0 \
    faiss-cpu==1.11.0.post1 \
    boto3==1.34.162 \
    python-dotenv==1.0.1 \
    pydantic==2.11.7 \
    scikit-learn==1.7.1

# Production stage - much smaller
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy source code (data files excluded via .dockerignore)
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PATH=/root/.local/bin:$PATH
ENV TRANSFORMERS_CACHE=/tmp
ENV HF_HOME=/tmp

EXPOSE 8000

# Use the full AI-powered API
CMD ["python", "-m", "uvicorn", "src.swipe_api:app", "--host", "0.0.0.0", "--port", "8000"]
