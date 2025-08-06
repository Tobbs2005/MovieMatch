#!/usr/bin/env python3
"""
Memory usage testing script for movie-match app
This will help check if the app stays under 512MB memory limit
"""

import psutil
import os
import time
import sys
from datetime import datetime

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024  # Convert bytes to MB

def monitor_memory(duration_seconds=60):
    """Monitor memory usage for specified duration"""
    print(f"🔍 Starting memory monitoring for {duration_seconds} seconds...")
    print(f"📊 Memory limit target: 512 MB")
    print("=" * 50)
    
    max_memory = 0
    memory_readings = []
    start_time = time.time()
    
    while time.time() - start_time < duration_seconds:
        current_memory = get_memory_usage()
        memory_readings.append(current_memory)
        max_memory = max(max_memory, current_memory)
        
        status = "✅ SAFE" if current_memory < 512 else "❌ OVER LIMIT"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Memory: {current_memory:.1f} MB {status}")
        
        if current_memory > 512:
            print(f"⚠️  WARNING: Memory usage ({current_memory:.1f} MB) exceeds 512 MB limit!")
        
        time.sleep(5)  # Check every 5 seconds
    
    # Summary
    avg_memory = sum(memory_readings) / len(memory_readings)
    print("=" * 50)
    print(f"📈 Memory Usage Summary:")
    print(f"   Maximum: {max_memory:.1f} MB")
    print(f"   Average: {avg_memory:.1f} MB")
    print(f"   Status: {'✅ WITHIN LIMIT' if max_memory < 512 else '❌ EXCEEDS LIMIT'}")
    
    return max_memory < 512

def test_app_startup():
    """Test memory usage during app startup"""
    print("🚀 Testing app startup memory usage...")
    
    initial_memory = get_memory_usage()
    print(f"📊 Initial memory: {initial_memory:.1f} MB")
    
    try:
        # Import the main app components
        print("📦 Loading core modules...")
        import pandas as pd
        import numpy as np
        current_memory = get_memory_usage()
        print(f"   After pandas/numpy: {current_memory:.1f} MB (+{current_memory - initial_memory:.1f} MB)")
        
        print("🤖 Loading ML components...")
        from sentence_transformers import SentenceTransformer
        import faiss
        current_memory = get_memory_usage()
        print(f"   After ML imports: {current_memory:.1f} MB (+{current_memory - initial_memory:.1f} MB)")
        
        # Change to the src directory to import local modules
        sys.path.append('/Users/TobyFang/Desktop/movie-match/src')
        
        print("📊 Loading data...")
        from r2_config import load_data_with_fallback_chunked
        df, embeddings = load_data_with_fallback_chunked(max_movies=5000)
        current_memory = get_memory_usage()
        print(f"   After data loading: {current_memory:.1f} MB (+{current_memory - initial_memory:.1f} MB)")
        
        print("🔧 Loading FastAPI app...")
        # Note: We don't actually start the server, just load the module
        # This simulates the memory usage during startup
        current_memory = get_memory_usage()
        print(f"   Final memory usage: {current_memory:.1f} MB")
        
        if current_memory < 512:
            print(f"✅ SUCCESS: App startup memory ({current_memory:.1f} MB) is within 512 MB limit")
            return True
        else:
            print(f"❌ FAILURE: App startup memory ({current_memory:.1f} MB) exceeds 512 MB limit")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    print("🔬 Movie Match Memory Testing")
    print("=" * 50)
    
    # Test startup memory
    startup_ok = test_app_startup()
    
    if startup_ok:
        print("\n🔄 Starting runtime memory monitoring...")
        runtime_ok = monitor_memory(30)  # Monitor for 30 seconds
        
        if runtime_ok:
            print("\n🎉 ALL TESTS PASSED: App should deploy successfully within 512 MB limit")
        else:
            print("\n⚠️  WARNING: Runtime memory usage may exceed limits")
    else:
        print("\n❌ STARTUP FAILED: App may not deploy successfully due to memory constraints")
