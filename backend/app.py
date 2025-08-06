"""
Main application entry point for Hugging Face Spaces
This file serves the FastAPI backend for the MovieMatch application
"""
import os
import sys

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

# Import the FastAPI app from swipe_api
from swipe_api import app

# This is the main application instance that Hugging Face Spaces will use
if __name__ == "__main__":
    import uvicorn
    # Use Hugging Face Spaces standard port
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
