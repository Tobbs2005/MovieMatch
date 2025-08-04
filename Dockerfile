# Optimized Docker image for Railway (data from R2, not local files)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/*

# Create requirements with full ML packages (data files excluded via .dockerignore)
RUN echo "fastapi==0.116.1" > requirements.txt && \
    echo "uvicorn==0.35.0" >> requirements.txt && \
    echo "pandas==2.3.1" >> requirements.txt && \
    echo "numpy==2.3.2" >> requirements.txt && \
    echo "sentence-transformers==5.0.0" >> requirements.txt && \
    echo "faiss-cpu==1.11.0.post1" >> requirements.txt && \
    echo "boto3==1.34.162" >> requirements.txt && \
    echo "python-dotenv==1.0.1" >> requirements.txt && \
    echo "pydantic==2.11.7" >> requirements.txt && \
    echo "scikit-learn==1.7.1" >> requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip cache purge && \
    rm -rf /root/.cache/pip

# Copy source code (excluding data files via .dockerignore)
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Use the original API (data will come from R2)
CMD ["python", "-m", "uvicorn", "src.swipe_api:app", "--host", "0.0.0.0", "--port", "8000"]
