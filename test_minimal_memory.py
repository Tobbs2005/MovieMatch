#!/usr/bin/env python3
"""
Test memory usage of ultra-minimal API
"""
import psutil
import os
import sys

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024

def test_minimal_api():
    """Test memory usage of ultra-minimal API"""
    print("🧪 Testing Ultra-Minimal API Memory Usage")
    print("=" * 50)
    
    initial_memory = get_memory_usage()
    print(f"📊 Initial memory: {initial_memory:.1f} MB")
    
    try:
        # Change to the project directory
        sys.path.append('/Users/TobyFang/Desktop/movie-match')
        
        print("📦 Loading ultra-minimal API...")
        import minimal_api
        
        current_memory = get_memory_usage()
        print(f"📊 After loading API: {current_memory:.1f} MB")
        print(f"📈 Memory increase: +{current_memory - initial_memory:.1f} MB")
        
        # Test that ML components are NOT loaded yet
        print("🔍 Testing lazy loading (ML components should not be loaded yet)...")
        if minimal_api.model is None:
            print("✅ ML components not loaded (good - lazy loading working)")
        else:
            print("⚠️  ML components already loaded")
        
        # Check if we're under limit
        if current_memory < 512:
            print(f"\n✅ SUCCESS: Ultra-minimal API ({current_memory:.1f} MB) is within 512 MB limit")
            print(f"📊 Remaining memory budget: {512 - current_memory:.1f} MB")
            return True
        else:
            print(f"\n❌ FAILURE: Ultra-minimal API ({current_memory:.1f} MB) still exceeds 512 MB limit")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal_api()
    
    if success:
        print("\n🎉 Ultra-minimal API should deploy successfully!")
        print("\n💡 Key optimizations applied:")
        print("   • Reduced dataset to 2000 movies (from 5000)")
        print("   • Lazy loading of ML components")
        print("   • Removed FAISS index (using numpy similarity)")
        print("   • Ultra-minimal columns and data types")
        print("   • Aggressive memory cleanup")
        print("   • Text-based search fallback")
    else:
        print("\n⚠️  Further optimization may be needed")
