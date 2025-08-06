"""
Configuration for Hugging Face Spaces deployment
This module provides utilities for running the MovieMatch backend on Hugging Face Spaces
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_spaces_environment():
    """
    Setup environment for Hugging Face Spaces
    """
    # Set environment variables for Spaces
    os.environ.setdefault('TRANSFORMERS_CACHE', '/tmp/transformers_cache')
    os.environ.setdefault('HF_HOME', '/tmp/hf_home')
    
    # Disable tokenizers parallelism to avoid warnings
    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    
    # Add src to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(current_dir, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    logger.info("Environment configured for Hugging Face Spaces")

def get_spaces_config():
    """
    Get configuration specific to Hugging Face Spaces
    """
    return {
        'host': '0.0.0.0',
        'port': int(os.environ.get('PORT', 7860)),
        'max_movies': int(os.environ.get('MAX_MOVIES', 2000)),  # Reduced for memory efficiency
        'enable_r2': os.environ.get('ENABLE_R2', 'false').lower() == 'true',
        'debug': os.environ.get('DEBUG', 'false').lower() == 'true'
    }
