"""
Memory-optimized API with AI recommendations but simple text search
Target: < 350MB memory usage
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

print("🔄 Loading optimized data...")

# === Optimized data loading ===
def load_optimized_data(max_movies=1500):  # Further reduced from 2000
    """Load dataset optimized for AI recommendations only"""
    try:
        # Add the src directory to path for importing r2_config
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # If we're already in src or somewhere else, try adding current dir
        if os.path.exists(os.path.join(current_dir, 'r2_config.py')):
            sys.path.insert(0, current_dir)
        elif os.path.exists(os.path.join(current_dir, '..', 'src', 'r2_config.py')):
            sys.path.insert(0, os.path.join(current_dir, '..', 'src'))
        
        print(f"🔄 Attempting to load from R2... (current dir: {current_dir})")
        
        # Try R2 first
        from r2_config import load_data_with_fallback_chunked
        df, embeddings = load_data_with_fallback_chunked(max_movies=max_movies)
        print("✅ Successfully loaded from R2!")
        
    except Exception as e:
        print(f"🔄 R2 failed ({str(e)}), using local fallback...")
        
        # Fallback to local data
        try:
            df = pd.read_csv('/Users/TobyFang/Desktop/movie-match/src/data/TMDB_movie_dataset_v11.csv')
            embeddings = np.load('/Users/TobyFang/Desktop/movie-match/src/data/movie_embeddings_v11.npy')
            
            # Select top movies by vote count and limit
            df = df.nlargest(max_movies, 'vote_count').reset_index(drop=True)
            embeddings = embeddings[:len(df)]
        except Exception as local_e:
            print(f"Local fallback failed: {local_e}")
            # Create dummy data if all else fails
            df = pd.DataFrame({
                'id': range(1, 101),
                'title': [f'Movie {i}' for i in range(1, 101)],
                'genres': ['Action'] * 100,
                'overview': ['Sample movie overview'] * 100
            })
            embeddings = np.random.random((100, 384)).astype('float32')
    
    # Ultra-aggressive column reduction - only absolutely essential for recommendations
    essential_columns = ['id', 'title', 'genres', 'overview']
    df = df[essential_columns].copy()
    
    # Aggressive data type optimization
    df['id'] = df['id'].astype('int32')
    df['genres'] = df['genres'].astype('category')
    
    # Truncate overview more aggressively - only need for basic similarity
    df['overview'] = df['overview'].fillna('').str[:80]  # Reduced from 100 to 80 chars
    
    # Use aggressive float precision
    embeddings = embeddings.astype('float32')
    
    # Multiple garbage collections
    gc.collect()
    gc.collect()
    
    return df, embeddings

# Load data
df, embeddings = load_optimized_data(max_movies=1500)  # Reduced from 2000
print(f"✅ Loaded {len(df)} movies (optimized for AI recommendations)")

# === Lazy Load ML Components (Only for Recommendations) ===
model = None
recommendation_index = None

def get_recommendation_components():
    """Lazy load ML components - only for recommendations"""
    global model, recommendation_index
    if model is None:
        print("🔄 Loading ML components for recommendations...")
        
        # Use CPU-only, minimal model
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2", device='cpu')
        
        # Simple numpy-based similarity for recommendations
        print("✅ Using numpy similarity for recommendations")
        recommendation_index = None  # We'll use numpy dot product
        
        gc.collect()
    return model, recommendation_index

# === FastAPI Setup ===
app = FastAPI(title="MovieMatch Optimized API")
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
        "message": "MovieMatch Optimized API",
        "movies_loaded": len(df),
        "features": {
            "ai_recommendations": True,
            "text_search": True,
            "ai_search": False  # Disabled to save memory
        }
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# === AI-Powered Recommendations ===
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
        return {"recommendations": recommendations, "method": "popular"}
    
    # For users with history, use AI recommendations
    try:
        model_instance, _ = get_recommendation_components()
        
        # Get embeddings for liked movies
        liked_indices = df[df['id'].isin(payload.liked_ids)].index.tolist()
        if liked_indices:
            # Create user profile from liked movies
            liked_embeddings = embeddings[liked_indices]
            user_profile = np.mean(liked_embeddings, axis=0)
            
            # Get available movie indices
            available_indices = available_df.index.tolist()
            if available_indices:
                # Calculate similarities
                available_embeddings = embeddings[available_indices]
                similarities = np.dot(available_embeddings, user_profile)
                
                # Get top recommendations
                top_indices = np.argsort(similarities)[-20:][::-1]
                recommended_movies = available_df.iloc[top_indices]
                
                return {
                    "recommendations": recommended_movies.to_dict('records'),
                    "method": "ai_collaborative"
                }
    except Exception as e:
        print(f"AI recommendation failed: {e}, falling back to genre-based")
    
    # Fallback to simple genre-based recommendations
    if payload.liked_ids:
        liked_movies = df[df['id'].isin(payload.liked_ids)]
        liked_genres = ' '.join(liked_movies['genres'].fillna('').astype(str))
        
        # Simple text-based similarity
        available_df['genre_similarity'] = available_df['genres'].fillna('').str.count('|'.join(liked_genres.split('|')[:3]))
        available_df = available_df.sort_values('genre_similarity', ascending=False)
    
    sample_size = min(20, len(available_df))
    recommendations = available_df.head(sample_size).to_dict('records')
    return {"recommendations": recommendations, "method": "genre_based"}

# === Simple Text Search (No AI) ===
@app.post("/search")
def search(payload: SearchPayload):
    """Text-based search only - no AI to save memory"""
    query = payload.query.lower()
    
    # Simple text search
    text_matches = df[
        df['title'].str.lower().str.contains(query, na=False) |
        df['overview'].str.lower().str.contains(query, na=False) |
        df['genres'].str.lower().str.contains(query, na=False)
    ]
    
    # Apply genre filter
    if payload.genre:
        text_matches = text_matches[text_matches['genres'].str.contains(payload.genre, case=False, na=False)]
    
    return {
        "results": text_matches.head(20).to_dict('records'),
        "method": "text_search",
        "note": "AI search disabled to optimize memory usage"
    }

# === Feedback endpoint (simplified) ===
@app.post("/feedback")
def feedback(payload: dict):
    """Simple feedback logging"""
    return {"status": "received", "message": "Feedback logged"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
