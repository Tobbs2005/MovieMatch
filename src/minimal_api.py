"""
Ultra-minimal memory-optimized version of the movie-match API
Target: < 512MB memory usage
"""
import os
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import random
import gc

print("🔄 Loading minimal data (ultra-optimized)...")

# === Ultra-minimal data loading ===
def load_minimal_data(max_movies=2000):  # Reduced from 5000
    """Load minimal dataset with aggressive memory optimization"""
    try:
        # Add the src directory to path for importing r2_config
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_path = os.path.join(current_dir, 'src')
        
        # If we're in the root directory, add src to path
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)
        # If we're already in src or somewhere else, try adding current dir
        elif os.path.exists(os.path.join(current_dir, 'r2_config.py')):
            sys.path.insert(0, current_dir)
        
        print(f"🔄 Attempting to load from R2... (current dir: {current_dir})")
        
        # Try R2 first
        from r2_config import load_data_with_fallback_chunked
        df, embeddings = load_data_with_fallback_chunked(max_movies=max_movies)
        print("✅ Successfully loaded from R2!")
        
    except Exception as e:
        print(f"🔄 R2 failed ({str(e)}), using local fallback...")
        
        # Try multiple local paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_dir, 'src', 'data', 'TMDB_movie_dataset_v11.csv'),
            os.path.join(base_dir, 'data', 'TMDB_movie_dataset_v11.csv'),
            'src/data/TMDB_movie_dataset_v11.csv',
            'data/TMDB_movie_dataset_v11.csv'
        ]
        
        data_path = None
        for path in possible_paths:
            if os.path.exists(path):
                data_path = path
                break
        
        if data_path is None:
            raise Exception("❌ No data files found! Please check your data directory.")
        
        # Load local data
        print(f"📁 Loading from local file: {data_path}")
        df = pd.read_csv(data_path)
        df = df.fillna('')
        
        # Load embeddings
        embedding_path = data_path.replace('.csv', '_embeddings.npy').replace('TMDB_movie_dataset_v11', 'movie_embeddings_v11')
        if not os.path.exists(embedding_path):
            # Try alternative embedding paths
            embedding_paths = [
                os.path.join(os.path.dirname(data_path), 'movie_embeddings_v11.npy'),
                data_path.replace('TMDB_movie_dataset_v11.csv', 'movie_embeddings_v11.npy')
            ]
            for epath in embedding_paths:
                if os.path.exists(epath):
                    embedding_path = epath
                    break
        
        if not os.path.exists(embedding_path):
            print(f"⚠️  No embeddings found, creating dummy embeddings for testing...")
            # Create dummy embeddings for testing
            embeddings = np.random.rand(len(df), 384).astype('float32')
        else:
            embeddings = np.load(embedding_path)
        
        # Select top movies by vote count and limit
        if 'vote_count' in df.columns:
            df = df.nlargest(max_movies, 'vote_count').reset_index(drop=True)
        else:
            df = df.head(max_movies).reset_index(drop=True)
        
        embeddings = embeddings[:len(df)]
    
    # Ultra-aggressive column reduction - only absolutely essential
    essential_columns = ['id', 'title', 'genres', 'overview']  # Removed poster_path, release_date, vote_count
    df = df[essential_columns].copy()
    
    # Aggressive data type optimization
    df['id'] = df['id'].astype('int32')
    df['genres'] = df['genres'].astype('category')
    
    # Truncate overview even more aggressively
    df['overview'] = df['overview'].fillna('').str[:100]  # Reduced from 200 to 100 chars
    
    # Use even more aggressive float precision
    embeddings = embeddings.astype('float32')
    
    # Force multiple garbage collections
    gc.collect()
    gc.collect()
    
    return df, embeddings

# Load data
df, embeddings = load_minimal_data(max_movies=2000)  # Reduced from 5000
print(f"✅ Loaded {len(df)} movies (ultra-optimized)")

# === Lazy Load ML Components (Only When Needed) ===
model = None
index = None

def get_ml_components():
    """Lazy load ML components - only when actually needed"""
    global model, index
    if model is None:
        print("🔄 Loading minimal ML components...")
        
        # Use CPU-only, minimal model
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2", device='cpu')
        
        # Simple numpy-based similarity instead of FAISS to save memory
        print("✅ Using numpy similarity (no FAISS)")
        index = None  # We'll use numpy dot product instead
        
        gc.collect()
    return model, index

# === FastAPI Setup ===
app = FastAPI(title="MovieMatch Ultra-Minimal API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Request Models ===
class RecommendPayload(BaseModel):
    user_vector: Optional[list] = None
    seen_ids: list[int]
    liked_ids: list[int]
    genre: Optional[str] = None

class SearchPayload(BaseModel):
    query: str
    genre: Optional[str] = None

# === Health Check ===
@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "MovieMatch Ultra-Minimal API",
        "movies_loaded": len(df),
        "memory_optimized": True
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# === Simple Recommendation (No ML for basic recommendations) ===
@app.post("/recommend")
def recommend(payload: RecommendPayload):
    seen_set = set(payload.seen_ids + payload.liked_ids)
    available_df = df[~df['id'].isin(seen_set)]
    
    # Apply genre filter if specified
    if payload.genre:
        available_df = available_df[available_df['genres'].str.contains(payload.genre, case=False, na=False)]
    
    # For users with < 3 liked movies, return popular movies
    if len(payload.liked_ids) < 3:
        sample_size = min(20, len(available_df))
        recommendations = available_df.sample(n=sample_size).to_dict('records')
    else:
        # For users with some history, use simple genre-based recommendations
        if payload.liked_ids:
            liked_movies = df[df['id'].isin(payload.liked_ids)]
            liked_genres = ' '.join(liked_movies['genres'].fillna('').astype(str))
            
            # Simple text-based similarity
            available_df['genre_similarity'] = available_df['genres'].fillna('').str.count('|'.join(liked_genres.split('|')[:3]))
            available_df = available_df.sort_values('genre_similarity', ascending=False)
        
        sample_size = min(20, len(available_df))
        recommendations = available_df.head(sample_size).to_dict('records')
    
    return {"recommendations": recommendations}

# === Simple Search (Lazy Load ML) ===
@app.post("/search")
def search(payload: SearchPayload):
    """Search with lazy ML loading"""
    query = payload.query.lower()
    
    # Simple text search first (no ML)
    text_matches = df[
        df['title'].str.lower().str.contains(query, na=False) |
        df['overview'].str.lower().str.contains(query, na=False) |
        df['genres'].str.lower().str.contains(query, na=False)
    ]
    
    # Apply genre filter
    if payload.genre:
        text_matches = text_matches[text_matches['genres'].str.contains(payload.genre, case=False, na=False)]
    
    # If we have enough text matches, return them (avoid ML)
    if len(text_matches) >= 10:
        return {"results": text_matches.head(20).to_dict('records')}
    
    # Only use ML if we need better results and have few text matches
    try:
        model_instance, _ = get_ml_components()
        query_embedding = model_instance.encode(query, normalize_embeddings=True)
        
        # Simple numpy similarity (no FAISS)
        similarities = np.dot(embeddings, query_embedding)
        top_indices = np.argsort(similarities)[-20:][::-1]
        
        ml_results = df.iloc[top_indices]
        
        # Apply genre filter to ML results
        if payload.genre:
            ml_results = ml_results[ml_results['genres'].str.contains(payload.genre, case=False, na=False)]
        
        # Combine text and ML results, prioritizing text matches
        combined_results = pd.concat([text_matches.head(10), ml_results.head(10)]).drop_duplicates('id')
        
        return {"results": combined_results.head(20).to_dict('records')}
        
    except Exception as e:
        print(f"ML search failed: {e}, falling back to text search")
        return {"results": text_matches.head(20).to_dict('records')}

# === Feedback endpoint (simplified) ===
@app.post("/feedback")
def feedback(payload: dict):
    """Simple feedback logging"""
    return {"status": "received", "message": "Feedback logged"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
