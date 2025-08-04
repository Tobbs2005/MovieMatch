"""
Lightweight version of swipe_api.py optimized for Docker deployment
Downloads models on startup to reduce image size
"""
import os
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import random
import time

# Global variables for lazy loading
df = None
embeddings = None
model = None
index = None

def load_data_and_models():
    """Lazy load data and models on first request"""
    global df, embeddings, model, index
    
    if df is not None:
        return df, embeddings, model, index
    
    print("🔄 Loading data and models (first request)...")
    
    try:
        # Import here to avoid issues if not available
        from sentence_transformers import SentenceTransformer
        import faiss
        from r2_config import load_data_with_fallback
        
        # Load data
        df, embeddings = load_data_with_fallback()
        
        # Combine metadata fields
        df['metadata'] = (
            df['genres'] + ' ' +
            df['keywords'] + ' ' +
            df['original_language'] + ' ' +
            df['production_companies'] + ' ' +
            df['spoken_languages']
        ).str.lower()
        
        # Load model (will download on first run)
        print("📥 Downloading sentence transformer model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Build FAISS index
        print("🔍 Building search index...")
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        
        print(f"✅ Loaded {len(df)} movies successfully")
        return df, embeddings, model, index
        
    except Exception as e:
        print(f"❌ Error loading data: {str(e)}")
        # Create minimal fallback data
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'title': ['The Matrix', 'Inception', 'Interstellar', 'The Dark Knight', 'Pulp Fiction'],
            'genres': ['Action, Sci-Fi', 'Action, Sci-Fi, Thriller', 'Adventure, Drama, Sci-Fi', 'Action, Crime, Drama', 'Crime, Drama'],
            'overview': [
                'A computer hacker learns about the true nature of reality.',
                'A thief who enters people\'s dreams to steal secrets.',
                'A team of explorers travel through a wormhole in space.',
                'Batman fights crime in Gotham City.',
                'The lives of two mob hitmen, a boxer, and others intertwine.'
            ],
            'release_date': ['1999-03-31', '2010-07-16', '2014-11-07', '2008-07-18', '1994-10-14'],
            'poster_path': ['/path1.jpg', '/path2.jpg', '/path3.jpg', '/path4.jpg', '/path5.jpg'],
            'vote_count': [20000, 15000, 12000, 25000, 18000],
            'original_language': ['en', 'en', 'en', 'en', 'en'],
            'keywords': ['matrix, reality', 'dreams, inception', 'space, exploration', 'batman, gotham', 'crime, pulp'],
            'production_companies': ['Warner Bros', 'Warner Bros', 'Paramount', 'Warner Bros', 'Miramax'],
            'spoken_languages': ['English', 'English', 'English', 'English', 'English'],
            'adult': [False, False, False, False, False],
            'metadata': [
                'action sci-fi en warner bros english',
                'action sci-fi thriller en warner bros english', 
                'adventure drama sci-fi en paramount english',
                'action crime drama en warner bros english',
                'crime drama en miramax english'
            ]
        })
        embeddings = np.random.rand(5, 384).astype('float32')
        model = None
        index = None
        
        return df, embeddings, model, index

# === FastAPI Setup ===
app = FastAPI(title="MovieMatch AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Health Check Endpoints ===
@app.get("/")
def health_check():
    """Health check endpoint - loads data on first call"""
    try:
        df_local, embeddings_local, _, _ = load_data_and_models()
        return {
            "status": "healthy",
            "message": "MovieMatch AI Backend is running",
            "movies_loaded": len(df_local),
            "embeddings_shape": list(embeddings_local.shape) if embeddings_local is not None else [0, 0]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error initializing: {str(e)}"
        }

@app.get("/health")
def health():
    """Simple health check"""
    return {"status": "ok"}

# === Request Models ===
class RecommendPayload(BaseModel):
    user_vector: Optional[list] = None
    seen_ids: list[int] = []
    liked_ids: list[int] = []
    genre: Optional[str] = None
    language: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    adult: Optional[bool] = None

class FeedbackPayload(BaseModel):
    user_vector: Optional[list] = None
    movie_id: int
    feedback: str

class SearchPayload(BaseModel):
    query: str
    genre: Optional[str] = None
    language: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    adult: Optional[bool] = None

# === Utility Functions ===
def passes_filters(movie, filters):
    """Check if movie passes all filters"""
    try:
        if filters.get('genre') and filters['genre'].lower() not in movie["genres"].lower():
            return False
        if filters.get('language') and movie["original_language"] != filters['language']:
            return False
        if filters.get('adult') is not None and bool(movie.get("adult", False)) != filters['adult']:
            return False
        
        # Year filters
        if filters.get('year_start') or filters.get('year_end'):
            try:
                year = pd.to_datetime(movie["release_date"], errors="coerce").year
                if filters.get('year_start') and (year is None or year < filters['year_start']):
                    return False
                if filters.get('year_end') and (year is None or year > filters['year_end']):
                    return False
            except:
                return False
        
        return True
    except:
        return True

def format_movie_response(movie, user_vector=None):
    """Format movie for API response"""
    return {
        "movie": {
            "movieId": int(movie["id"]),
            "title": movie["title"],
            "genres": movie["genres"],
            "overview": movie["overview"],
            "release_date": movie["release_date"],
            "poster_path": "https://image.tmdb.org/t/p/w185" + movie.get("poster_path", ""),
        },
        "user_vector": user_vector
    }

# === API Endpoints ===
@app.post("/recommend")
def recommend(payload: RecommendPayload):
    """Get movie recommendations"""
    try:
        df_local, embeddings_local, model_local, index_local = load_data_and_models()
        
        seen_set = set(payload.seen_ids + payload.liked_ids)
        
        # Onboarding mode: < 5 liked movies
        if len(payload.liked_ids) < 5:
            top_voted = df_local.sort_values(by="vote_count", ascending=False).head(50)
            sampled = top_voted.sample(n=min(20, len(top_voted)))
            
            for _, movie in sampled.iterrows():
                if movie['id'] not in seen_set and passes_filters(movie, payload.dict()):
                    return format_movie_response(movie)
        
        # Normal recommendation mode
        if len(payload.liked_ids) >= 1 and embeddings_local is not None:
            # Get taste vector from liked movies
            vectors = []
            for mid in payload.liked_ids:
                matching_indices = df_local.index[df_local["id"] == mid]
                if not matching_indices.empty:
                    vectors.append(embeddings_local[matching_indices[0]])
            
            if vectors:
                taste_vector = np.mean(vectors, axis=0)
                taste_vector = taste_vector / np.linalg.norm(taste_vector)
                similarity_scores = np.dot(embeddings_local, taste_vector)
                
                sorted_indices = np.argsort(similarity_scores)[::-1]
                
                for idx in sorted_indices:
                    movie = df_local.iloc[idx]
                    if movie["id"] in seen_set:
                        continue
                    
                    if passes_filters(movie, payload.dict()):
                        return format_movie_response(movie, taste_vector.tolist())
        
        # Fallback to popular movies
        popular_movies = df_local.sort_values(by="vote_count", ascending=False).head(30)
        for _, movie in popular_movies.iterrows():
            if movie['id'] not in seen_set and passes_filters(movie, payload.dict()):
                return format_movie_response(movie)
        
        return {"error": "No movies found matching the specified filters."}
        
    except Exception as e:
        print(f"Recommendation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@app.post("/feedback")
def feedback(_: FeedbackPayload):
    """Handle user feedback (stateless for now)"""
    return {"user_vector": None}

@app.post("/search")
def search(payload: SearchPayload):
    """Search movies"""
    try:
        df_local, _, _, _ = load_data_and_models()
        
        query_lower = payload.query.lower()
        
        # Keyword search
        results = df_local[
            df_local["title"].str.lower().str.contains(query_lower, na=False) |
            df_local["overview"].str.lower().str.contains(query_lower, na=False) |
            df_local["genres"].astype(str).str.lower().str.contains(query_lower, na=False)
        ]
        
        # Apply filters
        filtered_results = results.copy()
        if payload.genre:
            filtered_results = filtered_results[filtered_results["genres"].astype(str).str.lower().str.contains(payload.genre.lower(), na=False)]
        if payload.language:
            filtered_results = filtered_results[filtered_results["original_language"] == payload.language]
        
        # Sort by relevance
        filtered_results = filtered_results.sort_values("vote_count", ascending=False)
        top_matches = filtered_results.head(8).to_dict(orient="records")
        
        return {
            "movies": [
                {
                    "title": m.get("title", "Untitled"),
                    "overview": m.get("overview", "No overview."),
                    "genres": m.get("genres", "N/A"),
                    "release_date": m.get("release_date", "N/A"),
                    "poster_path": "https://image.tmdb.org/t/p/w185" + m.get("poster_path", ""),
                    "movieId": int(m["id"]),
                }
                for m in top_matches
            ]
        }
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
