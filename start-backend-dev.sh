#!/bin/bash

# Start the FastAPI backend server for development
echo "Starting MovieMatch AI Backend..."

# Activate virtual environment
source venv/bin/activate

# Start the server with reload for development
echo "Starting FastAPI server on http://localhost:8000"
cd src && python -m uvicorn swipe_api:app --reload --host 0.0.0.0 --port 8000
