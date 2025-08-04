"""
Ultra-minimal API for Railway deployment
Removes ML dependencies to fit under 4GB Docker limit
"""
import os
import json
import random
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Try to import R2 config
try:
    from src.r2_config import load_data_with_fallback
    USE_R2 = True
except:
    USE_R2 = False

# Global data storage
movie_data = None

def load_movies():
    """Load movie data from R2 or fallback to mock data"""
    global movie_data
    
    if movie_data is not None:
        return movie_data
    
    if USE_R2:
        try:
            print("🔄 Loading data from R2...")
            df, _ = load_data_with_fallback()
            movie_data = df.to_dict('records')
            print(f"✅ Loaded {len(movie_data)} movies from R2")
            return movie_data
        except Exception as e:
            print(f"❌ R2 failed: {e}")
    
    # Fallback to mock data
    print("📝 Using mock movie data")
    movie_data = [
        {
            "id": 1, "title": "The Matrix", "genres": "Action, Sci-Fi",
            "overview": "A computer hacker learns about reality.", "release_date": "1999-03-31",
            "poster_path": "/path1.jpg", "vote_count": 20000, "original_language": "en", "adult": False
        },
        {
            "id": 2, "title": "Inception", "genres": "Action, Sci-Fi, Thriller", 
            "overview": "A thief enters dreams.", "release_date": "2010-07-16",
            "poster_path": "/path2.jpg", "vote_count": 15000, "original_language": "en", "adult": False
        },
        {
            "id": 3, "title": "Interstellar", "genres": "Adventure, Drama, Sci-Fi",
            "overview": "Space exploration story.", "release_date": "2014-11-07", 
            "poster_path": "/path3.jpg", "vote_count": 12000, "original_language": "en", "adult": False
        },
        {
            "id": 4, "title": "The Dark Knight", "genres": "Action, Crime, Drama",
            "overview": "Batman fights crime in Gotham.", "release_date": "2008-07-18",
            "poster_path": "/path4.jpg", "vote_count": 25000, "original_language": "en", "adult": False
        },
        {
            "id": 5, "title": "Pulp Fiction", "genres": "Crime, Drama",
            "overview": "Interconnected criminal stories.", "release_date": "1994-10-14",
            "poster_path": "/path5.jpg", "vote_count": 18000, "original_language": "en", "adult": False
        }
    ]
    return movie_data

# FastAPI setup
app = FastAPI(title="MovieMatch AI Minimal", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class RecommendPayload(BaseModel):
    user_vector: Optional[list] = None
    seen_ids: list[int] = []
    liked_ids: list[int] = []
    genre: Optional[str] = None
    language: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    adult: Optional[bool] = None

class SearchPayload(BaseModel):
    query: str
    genre: Optional[str] = None
    language: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    adult: Optional[bool] = None

class FeedbackPayload(BaseModel):
    user_vector: Optional[list] = None
    movie_id: int
    feedback: str

def passes_filters(movie, filters):
    """Check if movie passes filters"""
    try:
        if filters.get('genre') and filters['genre'].lower() not in movie.get("genres", "").lower():
            return False
        if filters.get('language') and movie.get("original_language") != filters['language']:
            return False
        if filters.get('adult') is not None and bool(movie.get("adult", False)) != filters['adult']:
            return False
        
        # Year filtering
        if filters.get('year_start') or filters.get('year_end'):
            try:
                year = int(movie.get("release_date", "")[:4]) if movie.get("release_date") else None
                if filters.get('year_start') and (year is None or year < filters['year_start']):
                    return False
                if filters.get('year_end') and (year is None or year > filters['year_end']):
                    return False
            except:
                return False
        
        return True
    except:
        return True

# Health endpoints
@app.get("/")
@app.get("/health")
def health_check():
    """Health check"""
    movies = load_movies()
    return {
        "status": "healthy",
        "message": "MovieMatch AI Minimal is running",
        "movies_loaded": len(movies),
        "mode": "R2" if USE_R2 else "mock"
    }

# API endpoints
@app.post("/recommend")
def recommend(payload: RecommendPayload):
    """Get movie recommendations (simplified without ML)"""
    try:
        movies = load_movies()
        seen_set = set(payload.seen_ids + payload.liked_ids)
        
        # Simple recommendation: popular movies first, then random
        available_movies = [m for m in movies if m["id"] not in seen_set]
        
        # Apply filters
        filtered_movies = [m for m in available_movies if passes_filters(m, payload.dict())]
        
        if not filtered_movies:
            return {"error": "No movies found matching filters"}
        
        # Sort by vote count (popularity) and pick first
        filtered_movies.sort(key=lambda x: x.get("vote_count", 0), reverse=True)
        movie = filtered_movies[0]
        
        return {
            "movie": {
                "movieId": movie["id"],
                "title": movie["title"],
                "genres": movie["genres"],
                "overview": movie["overview"],
                "release_date": movie["release_date"],
                "poster_path": "https://image.tmdb.org/t/p/w185" + movie.get("poster_path", ""),
            },
            "user_vector": None
        }
        
    except Exception as e:
        return {"error": f"Recommendation failed: {str(e)}"}

@app.post("/search")
def search(payload: SearchPayload):
    """Search movies (simple text matching)"""
    try:
        movies = load_movies()
        query_lower = payload.query.lower()
        
        # Simple text search
        results = []
        for movie in movies:
            if (query_lower in movie.get("title", "").lower() or 
                query_lower in movie.get("overview", "").lower() or
                query_lower in movie.get("genres", "").lower()):
                if passes_filters(movie, payload.dict()):
                    results.append(movie)
        
        # Sort by popularity and take top 8
        results.sort(key=lambda x: x.get("vote_count", 0), reverse=True)
        results = results[:8]
        
        return {
            "movies": [
                {
                    "title": m["title"],
                    "overview": m["overview"],
                    "genres": m["genres"],
                    "release_date": m["release_date"],
                    "poster_path": "https://image.tmdb.org/t/p/w185" + m.get("poster_path", ""),
                    "movieId": m["id"],
                }
                for m in results
            ]
        }
        
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

@app.post("/feedback")
def feedback(payload: FeedbackPayload):
    """Handle feedback (stateless)"""
    return {"user_vector": None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
