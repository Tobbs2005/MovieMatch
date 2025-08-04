"""
Cloudflare R2 Configuration and Data Loading
"""
import os
import boto3
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from typing import Optional
import tempfile
from pathlib import Path

# Load environment variables
load_dotenv()

class R2DataLoader:
    def __init__(self):
        """Initialize R2 client with Cloudflare credentials"""
        self.account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
        self.access_key = os.getenv('R2_ACCESS_KEY_ID')
        self.secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('R2_BUCKET_NAME', 'movie-match-data')
        self.endpoint_url = f'https://{self.account_id}.r2.cloudflarestorage.com'
        
        if not all([self.account_id, self.access_key, self.secret_key]):
            raise ValueError("Missing R2 credentials. Please set CLOUDFLARE_ACCOUNT_ID, R2_ACCESS_KEY_ID, and R2_SECRET_ACCESS_KEY environment variables.")
        
        # Initialize boto3 client for R2
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='auto'  # R2 uses 'auto' for region
        )
        
        # Cache directory for downloaded files
        self.cache_dir = Path(tempfile.gettempdir()) / 'movie_match_cache'
        self.cache_dir.mkdir(exist_ok=True)
    
    def download_file(self, key: str, local_path: Optional[str] = None) -> str:
        """
        Download a file from R2 bucket
        
        Args:
            key: The file key in R2 bucket
            local_path: Optional local path to save file
            
        Returns:
            Path to the downloaded file
        """
        if local_path is None:
            local_path = self.cache_dir / key
        else:
            local_path = Path(local_path)
        
        # Create directory if it doesn't exist
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists locally and is recent
        if local_path.exists():
            print(f"Using cached file: {local_path}")
            return str(local_path)
        
        try:
            print(f"Downloading {key} from R2...")
            self.s3_client.download_file(self.bucket_name, key, str(local_path))
            print(f"Downloaded to: {local_path}")
            return str(local_path)
        except Exception as e:
            raise Exception(f"Failed to download {key} from R2: {str(e)}")
    
    def upload_file(self, local_path: str, key: str) -> bool:
        """
        Upload a file to R2 bucket
        
        Args:
            local_path: Path to local file
            key: The file key to use in R2 bucket
            
        Returns:
            Success status
        """
        try:
            print(f"Uploading {local_path} to R2 as {key}...")
            self.s3_client.upload_file(local_path, self.bucket_name, key)
            print(f"Successfully uploaded {key}")
            return True
        except Exception as e:
            print(f"Failed to upload {key} to R2: {str(e)}")
            return False
    
    def load_movie_data(self) -> pd.DataFrame:
        """Load movie dataset from R2"""
        csv_path = self.download_file('TMDB_movie_dataset_v11.csv')
        df = pd.read_csv(csv_path)
        df.fillna('', inplace=True)
        print(f"Loaded {len(df)} movies from R2")
        return df
    
    def load_embeddings(self) -> np.ndarray:
        """Load movie embeddings from R2"""
        embeddings_path = self.download_file('movie_embeddings_v11.npy')
        embeddings = np.load(embeddings_path)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        print(f"Loaded embeddings shape: {embeddings.shape}")
        return embeddings
    
    def file_exists(self, key: str) -> bool:
        """Check if a file exists in R2 bucket"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except:
            return False
    
    def list_files(self, prefix: str = '') -> list:
        """List files in R2 bucket with optional prefix"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            return [obj['Key'] for obj in response.get('Contents', [])]
        except Exception as e:
            print(f"Failed to list files: {str(e)}")
            return []

# Fallback to local files if R2 is not configured
def load_data_with_fallback():
    """
    Load data from R2 if configured, otherwise fall back to local files
    """
    try:
        # Try to load from R2
        r2_loader = R2DataLoader()
        df = r2_loader.load_movie_data()
        embeddings = r2_loader.load_embeddings()
        print("✅ Successfully loaded data from Cloudflare R2")
        return df, embeddings
    except Exception as e:
        print(f"⚠️  R2 loading failed: {str(e)}")
        print("📁 Falling back to local files...")
        
        # Fallback to local files
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, "data", "TMDB_movie_dataset_v11.csv")
        embedding_path = os.path.join(base_dir, "data", "movie_embeddings_v11.npy")
        
        if not os.path.exists(data_path) or not os.path.exists(embedding_path):
            raise Exception(f"Neither R2 nor local data files are available. Please set up R2 credentials or place data files in {os.path.join(base_dir, 'data/')}")
        
        df = pd.read_csv(data_path)
        df.fillna('', inplace=True)
        embeddings = np.load(embedding_path)
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        print("✅ Successfully loaded data from local files")
        return df, embeddings

# Memory-efficient loading for cloud deployment
def load_data_with_fallback_chunked(max_movies=5000):
    """
    Load data from R2 if configured, with memory-efficient chunked processing
    Only keeps top movies by vote count to stay within memory limits
    """
    try:
        # Try to load from R2
        r2_loader = R2DataLoader()
        
        # Download and process CSV in chunks
        csv_path = r2_loader.download_file('TMDB_movie_dataset_v11.csv')
        
        print(f"📊 Processing dataset in chunks to find top {max_movies} movies...")
        
        # First pass: find top movies by vote_count without loading everything
        top_movies_df = None
        chunk_size = 10000
        
        for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
            chunk = chunk.fillna('')
            # Only keep movies with reasonable vote counts
            chunk = chunk[chunk['vote_count'] > 10]
            
            if top_movies_df is None:
                top_movies_df = chunk.nlargest(max_movies, 'vote_count')
            else:
                # Combine and keep only top movies
                combined = pd.concat([top_movies_df, chunk])
                top_movies_df = combined.nlargest(max_movies, 'vote_count')
        
        # Get the indices of the top movies for embeddings
        df_full = pd.read_csv(csv_path)
        df_full = df_full.fillna('')
        top_indices = df_full[df_full['id'].isin(top_movies_df['id'])].index.tolist()
        
        # Load only the embeddings for top movies
        embeddings_path = r2_loader.download_file('movie_embeddings_v11.npy')
        embeddings_full = np.load(embeddings_path)
        embeddings = embeddings_full[top_indices]
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        # Clean up
        del df_full, embeddings_full
        import gc
        gc.collect()
        
        print(f"✅ Successfully loaded top {len(top_movies_df)} movies from R2 (memory optimized)")
        return top_movies_df.reset_index(drop=True), embeddings
        
    except Exception as e:
        print(f"⚠️  R2 chunked loading failed: {str(e)}")
        return load_data_with_fallback_simple(max_movies)

def load_data_with_fallback_simple(max_movies=5000):
    """Fallback to local files with memory optimization"""
    print("📁 Falling back to local files...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "TMDB_movie_dataset_v11.csv")
    embedding_path = os.path.join(base_dir, "data", "movie_embeddings_v11.npy")
    
    if not os.path.exists(data_path) or not os.path.exists(embedding_path):
        raise Exception(f"Neither R2 nor local data files are available")
    
    # Load and process in chunks for local files too
    print(f"📊 Processing local dataset in chunks to find top {max_movies} movies...")
    
    top_movies_df = None
    chunk_size = 10000
    
    for chunk in pd.read_csv(data_path, chunksize=chunk_size):
        chunk = chunk.fillna('')
        chunk = chunk[chunk['vote_count'] > 10]
        
        if top_movies_df is None:
            top_movies_df = chunk.nlargest(max_movies, 'vote_count')
        else:
            combined = pd.concat([top_movies_df, chunk])
            top_movies_df = combined.nlargest(max_movies, 'vote_count')
    
    # Get indices and load corresponding embeddings
    df_full = pd.read_csv(data_path)
    df_full = df_full.fillna('')
    top_indices = df_full[df_full['id'].isin(top_movies_df['id'])].index.tolist()
    
    embeddings_full = np.load(embedding_path)
    embeddings = embeddings_full[top_indices]
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Clean up
    del df_full, embeddings_full
    import gc
    gc.collect()
    
    print(f"✅ Successfully loaded top {len(top_movies_df)} movies from local files (memory optimized)")
    return top_movies_df.reset_index(drop=True), embeddings
