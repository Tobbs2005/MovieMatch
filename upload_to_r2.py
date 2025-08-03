#!/usr/bin/env python3
"""
Script to upload movie data and embeddings to Cloudflare R2
Run this once to upload your local data files to R2
"""

import os
import sys
from pathlib import Path

# Add src directory to path to import r2_config
sys.path.append(str(Path(__file__).parent / 'src'))

from r2_config import R2DataLoader

def upload_data_to_r2():
    """Upload local movie data files to R2 bucket"""
    try:
        r2_loader = R2DataLoader()
        
        # Paths to local data files
        base_dir = Path(__file__).parent / 'src' / 'data'
        csv_file = base_dir / 'TMDB_movie_dataset_v11.csv'
        embeddings_file = base_dir / 'movie_embeddings_v11.npy'
        
        # Check if local files exist
        if not csv_file.exists():
            print(f"❌ Movie dataset not found: {csv_file}")
            return False
            
        if not embeddings_file.exists():
            print(f"❌ Embeddings file not found: {embeddings_file}")
            return False
        
        print("🚀 Starting upload to Cloudflare R2...")
        
        # Upload CSV file
        success1 = r2_loader.upload_file(
            str(csv_file), 
            'TMDB_movie_dataset_v11.csv'
        )
        
        # Upload embeddings file
        success2 = r2_loader.upload_file(
            str(embeddings_file), 
            'movie_embeddings_v11.npy'
        )
        
        if success1 and success2:
            print("✅ Successfully uploaded all files to R2!")
            print(f"📊 Dataset: TMDB_movie_dataset_v11.csv")
            print(f"🧠 Embeddings: movie_embeddings_v11.npy")
            print(f"🪣 Bucket: {r2_loader.bucket_name}")
            return True
        else:
            print("❌ Some uploads failed")
            return False
            
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return False

def list_r2_files():
    """List files currently in R2 bucket"""
    try:
        r2_loader = R2DataLoader()
        files = r2_loader.list_files()
        
        if files:
            print(f"📁 Files in R2 bucket '{r2_loader.bucket_name}':")
            for file in files:
                print(f"  - {file}")
        else:
            print("📁 No files found in R2 bucket")
            
    except Exception as e:
        print(f"❌ Failed to list files: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage movie data in Cloudflare R2")
    parser.add_argument("action", choices=["upload", "list"], 
                       help="Action to perform: upload local files or list R2 files")
    
    args = parser.parse_args()
    
    if args.action == "upload":
        upload_data_to_r2()
    elif args.action == "list":
        list_r2_files()
