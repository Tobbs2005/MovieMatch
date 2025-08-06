#!/usr/bin/env python3
"""
Memory estimation script for movie-match app
Estimates memory usage based on data structures
"""

import sys
import os

def estimate_memory_usage():
    """Estimate memory usage for the movie-match app"""
    
    print("🧮 Memory Usage Estimation for Movie Match App")
    print("=" * 60)
    
    # Estimated memory usage for different components
    estimates = {
        "Python Base Runtime": 25,  # MB
        "FastAPI + Uvicorn": 15,    # MB
        "Pandas DataFrame (5000 movies, 7 columns)": 10,  # MB
        "Movie Embeddings (5000 x 384 float32)": 7.5,    # MB (5000 * 384 * 4 bytes)
        "SentenceTransformer Model (all-MiniLM-L6-v2)": 90,  # MB
        "FAISS Index": 8,           # MB
        "Query Cache + Other Variables": 10,  # MB
        "OS/System Overhead": 20,   # MB
    }
    
    print("📊 Component Memory Estimates:")
    total = 0
    for component, size in estimates.items():
        print(f"   {component:.<45} {size:>6.1f} MB")
        total += size
    
    print("-" * 60)
    print(f"   {'TOTAL ESTIMATED USAGE':.<45} {total:>6.1f} MB")
    print("-" * 60)
    
    # Safety analysis
    limit = 512
    safety_margin = limit * 0.1  # 10% safety margin
    effective_limit = limit - safety_margin
    
    print(f"\n🎯 Memory Limit Analysis:")
    print(f"   Deployment Limit: {limit} MB")
    print(f"   Safety Margin (10%): {safety_margin} MB")
    print(f"   Effective Limit: {effective_limit} MB")
    print(f"   Estimated Usage: {total} MB")
    print(f"   Remaining: {effective_limit - total:+.1f} MB")
    
    if total <= effective_limit:
        print(f"\n✅ SAFE TO DEPLOY: Estimated usage ({total} MB) is within safe limits")
        return True
    elif total <= limit:
        print(f"\n⚠️  CAUTION: Estimated usage ({total} MB) is close to limit but may work")
        return True
    else:
        print(f"\n❌ RISK: Estimated usage ({total} MB) exceeds limit ({limit} MB)")
        return False

def analyze_data_optimization():
    """Analyze current data optimization strategies"""
    
    print("\n🔧 Current Memory Optimizations:")
    optimizations = [
        "✅ Limited to 5000 movies (down from full dataset)",
        "✅ Using essential columns only (7 columns)",
        "✅ Aggressive data type optimization (int32, category)",
        "✅ Truncated overview text to 200 chars",
        "✅ Using float32 embeddings (not float64)",
        "✅ Lazy loading of ML components",
        "✅ Garbage collection after data loading",
        "✅ Using efficient FAISS index",
        "✅ LRU cache for query embeddings (limited size)",
    ]
    
    for opt in optimizations:
        print(f"   {opt}")
    
    print("\n💡 Additional Optimization Suggestions:")
    suggestions = [
        "Consider reducing model size further (e.g., all-MiniLM-L12-v2 → distilbert-base)",
        "Implement streaming data loading if needed",
        "Use memory mapping for embeddings if file-based",
        "Consider quantizing embeddings to int8 if accuracy allows",
        "Monitor actual memory usage in production",
    ]
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")

if __name__ == "__main__":
    safe_to_deploy = estimate_memory_usage()
    analyze_data_optimization()
    
    print("\n" + "=" * 60)
    if safe_to_deploy:
        print("🚀 RECOMMENDATION: Proceed with deployment")
    else:
        print("⛔ RECOMMENDATION: Further optimization needed before deployment")
