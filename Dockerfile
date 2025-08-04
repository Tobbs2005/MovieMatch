# Ultra-lightweight Docker image for Railway
FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create ultra-minimal requirements
RUN echo "fastapi==0.116.1" > requirements-ultra.txt && \
    echo "uvicorn==0.35.0" >> requirements-ultra.txt && \
    echo "pandas==2.3.1" >> requirements-ultra.txt && \
    echo "numpy==2.3.2" >> requirements-ultra.txt && \
    echo "sentence-transformers==5.0.0" >> requirements-ultra.txt && \
    echo "faiss-cpu==1.11.0.post1" >> requirements-ultra.txt && \
    echo "boto3==1.34.162" >> requirements-ultra.txt && \
    echo "python-dotenv==1.0.1" >> requirements-ultra.txt && \
    echo "pydantic==2.11.7" >> requirements-ultra.txt && \
    echo "scikit-learn==1.7.1" >> requirements-ultra.txt

# Install minimal dependencies
RUN pip install --no-cache-dir -r requirements-ultra.txt && \
    pip cache purge

# Copy source code
COPY src/ ./src/

# Set environment variables to reduce cache usage
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/tmp
ENV HF_HOME=/tmp
ENV TORCH_HOME=/tmp

EXPOSE 8000

# Use the lite version of the API
CMD ["python", "-m", "uvicorn", "src.swipe_api_lite:app", "--host", "0.0.0.0", "--port", "8000"]
