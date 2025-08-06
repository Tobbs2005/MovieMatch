# Use Python 3.11 slim image for better performance
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV TRANSFORMERS_CACHE=/tmp/transformers_cache
ENV HF_HOME=/tmp/hf_home
ENV TOKENIZERS_PARALLELISM=false

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_spaces.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_spaces.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /tmp/transformers_cache /tmp/hf_home

# Expose port
EXPOSE 7860

# Run the application
CMD ["python", "app.py"]
