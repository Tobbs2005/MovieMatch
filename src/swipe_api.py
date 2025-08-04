import os
import numpy as np
import pandas as pd
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss
import random
from functools import lru_cache
import time

# Import R2 data loader
from r2_config import load_data_with_fallback_chunked

# === Load Data (R2 or Local Fallback) - Memory Optimized ===
print("🔄 Loading data with memory optimization...")
df, embeddings = load_data_with_fallback_chunked(max_movies=15000)

# Additional optimizations
print("�️ Final memory optimizations...")

# Keep only minimal essential columns
essential_columns = ['id', 'title', 'genres', 'overview', 'release_date', 'poster_path', 'vote_count']
df = df[essential_columns].copy()

# Optimize data types aggressively
df['id'] = df['id'].astype('int32')
df['vote_count'] = df['vote_count'].astype('int32')

# Use category for repetitive string data
if 'genres' in df.columns:
    df['genres'] = df['genres'].astype('category')

# Truncate long overview text to save memory
if 'overview' in df.columns:
    df['overview'] = df['overview'].fillna('').str[:200]  # Max 200 chars

# Optimize embeddings memory (use float32)
embeddings = embeddings.astype('float32')

# Force garbage collection
import gc
gc.collect()

print(f"✅ Loaded {len(df)} movies, memory optimized")
import gc
gc.collect()

print(f"✅ Loaded {len(df)} movies, aggressively memory optimized")

# === Lazy Load ML Components ===
model = None
index = None

def get_ml_components():
    """Lazy load ML components on first use with aggressive memory optimization"""
    global model, index
    if model is None:
        print("🔄 Loading minimal sentence transformer model...")
        # Use the smallest possible model for memory efficiency
        model = SentenceTransformer("all-MiniLM-L6-v2", device='cpu')
        
        print("🔍 Building compact FAISS index...")
        # Use more memory-efficient index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        
        # Add embeddings in smaller batches to manage memory
        batch_size = 1000
        for i in range(0, len(embeddings), batch_size):
            batch = embeddings[i:i+batch_size]
            index.add(batch)
        
        # Aggressive garbage collection
        import gc
        gc.collect()
        
        print("✅ ML components ready (aggressively optimized)")
    return model, index

# === Query Cache for Performance ===
query_cache: Dict[str, Any] = {}
CACHE_TTL = 300  # 5 minutes
MAX_CACHE_SIZE = 100

@lru_cache(maxsize=50)
def get_query_embedding(query: str) -> np.ndarray:
    """Cache query embeddings to avoid recomputation"""
    model_instance, _ = get_ml_components()
    return model_instance.encode(query, normalize_embeddings=True)

# === FastAPI Setup ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Health Check Endpoint ===
@app.get("/")
def health_check():
    """Health check endpoint for Railway and other platforms"""
    return {
        "status": "healthy",
        "message": "MovieMatch AI Backend is running",
        "movies_loaded": len(df),
        "embeddings_shape": list(embeddings.shape)
    }

@app.get("/health")
def health():
    """Alternative health check endpoint"""
    return {"status": "ok"}

# === Request Models ===
class RecommendPayload(BaseModel):
    user_vector: Optional[list] = None
    seen_ids: list[int]
    liked_ids: list[int]
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

# === Recommendation Endpoint ===
@app.post("/recommend")
def recommend(payload: RecommendPayload):
    seen_set = set(payload.seen_ids + payload.liked_ids)

    # Onboarding mode: < 5 liked movies
    if len(payload.liked_ids) < 5:
        # Use more memory-efficient sampling
        top_indices = df['vote_count'].nlargest(100).index
        sample_size = min(30, len(top_indices))
        sampled_indices = np.random.choice(top_indices, size=sample_size, replace=False)

        for idx in sampled_indices:
            movie = df.iloc[idx]
            if movie['id'] not in seen_set:
                # Apply filters in onboarding mode
                if payload.genre and payload.genre.lower() not in movie["genres"].lower():
                    continue
                
                # Simplified year parsing for memory efficiency
                try:
                    year = int(movie["release_date"][:4]) if movie["release_date"] and len(movie["release_date"]) >= 4 else None
                except:
                    year = None

                if payload.year_start and (year is None or year < payload.year_start):
                    continue
                if payload.year_end and (year is None or year > payload.year_end):
                    continue

                return {
                    "movie": {
                        "movieId": int(movie["id"]),
                        "title": movie["title"],
                        "genres": movie["genres"],
                        "overview": movie["overview"],
                        "release_date": movie["release_date"],
                        "poster_path": "https://image.tmdb.org/t/p/w185" + movie.get("poster_path", ""),
                    },
                    "user_vector": None
                }
        
        print(f"No onboarding movies found matching filters, proceeding to normal recommendation mode")

    # Normal mode: Use collaborative filtering with memory optimization
    if len(payload.liked_ids) >= 1:
        # More memory-efficient vector computation
        liked_indices = []
        for mid in payload.liked_ids:
            matches = df.index[df["id"] == mid]
            if len(matches) > 0:
                liked_indices.append(matches[0])
        
        if liked_indices:
            # Use numpy operations for efficiency
            liked_embeddings = embeddings[liked_indices]
            taste_vector = np.mean(liked_embeddings, axis=0)
            taste_vector = taste_vector / np.linalg.norm(taste_vector)
            
            # Compute similarities in batches to save memory
            similarity_scores = np.dot(embeddings, taste_vector)

        # Apply soft penalty for disliked movies
        disliked_ids = list(set(payload.seen_ids) - set(payload.liked_ids))
        penalty_weight = 0.1
        for mid in disliked_ids:
            idx = df.index[df["id"] == mid]
            if not idx.empty:
                disliked_vec = embeddings[idx[0]]
                sims = np.dot(embeddings, disliked_vec)
                similarity_scores -= penalty_weight * sims

        sorted_indices = np.argsort(similarity_scores)[::-1]
        genre_counts = {}

        for idx in sorted_indices:
            movie = df.iloc[idx]
            if movie["id"] in seen_set:
                continue

            if payload.genre and payload.genre.lower() not in movie["genres"].lower():
                continue
            if payload.language and movie["original_language"] != payload.language:
                continue
            if payload.adult is not None and bool(movie.get("adult", False)) != payload.adult:
                continue

            try:
                year = pd.to_datetime(movie["release_date"], errors="coerce").year
            except:
                year = None

            if payload.year_start and (year is None or year < payload.year_start):
                continue
            if payload.year_end and (year is None or year > payload.year_end):
                continue

            movie_genres = movie["genres"].lower().split(',')
            primary_genre = movie_genres[0].strip() if movie_genres else None
            if primary_genre:
                genre_counts[primary_genre] = genre_counts.get(primary_genre, 0) + 1
                if genre_counts[primary_genre] > 5:
                    continue

            return {
                "movie": {
                    "movieId": int(movie["id"]),
                    "title": movie["title"],
                    "genres": movie["genres"],
                    "overview": movie["overview"],
                    "release_date": movie["release_date"],
                    "poster_path": "https://image.tmdb.org/t/p/w185" + movie.get("poster_path", ""),
                },
                "user_vector": taste_vector.tolist()
            }

        return {"error": "No more unseen movies matching the filters."}
    
    # Fallback for users with no liked movies and restrictive filters
    # Return any popular movie that matches filters
    else:
        popular_movies = df.sort_values(by="vote_count", ascending=False).head(200)
        for _, movie in popular_movies.iterrows():
            if movie['id'] not in seen_set:
                # Apply filters
                if payload.genre and payload.genre.lower() not in movie["genres"].lower():
                    continue
                if payload.language and movie["original_language"] != payload.language:
                    continue
                if payload.adult is not None and bool(movie.get("adult", False)) != payload.adult:
                    continue

                try:
                    year = pd.to_datetime(movie["release_date"], errors="coerce").year
                except:
                    year = None

                if payload.year_start and (year is None or year < payload.year_start):
                    continue
                if payload.year_end and (year is None or year > payload.year_end):
                    continue

                return {
                    "movie": {
                        "movieId": int(movie["id"]),
                        "title": movie["title"],
                        "genres": movie["genres"],
                        "overview": movie["overview"],
                        "release_date": movie["release_date"],
                        "poster_path": "https://image.tmdb.org/t/p/w185" + movie.get("poster_path", ""),
                    },
                    "user_vector": None
                }
        
        return {"error": "No movies found matching the specified filters."}

# === Feedback Endpoint ===
@app.post("/feedback")
def feedback(_: FeedbackPayload):
    return {"user_vector": None}  # now stateless

# === Search Endpoint ===

@app.post("/search")
def hybrid_search(payload: SearchPayload):
    start_time = time.time()
    query_lower = payload.query.lower()
    genre_lower = payload.genre.lower() if payload.genre else None

    # --- Fast Keyword Search First ---
    keyword_results = df[
        df["title"].str.lower().str.contains(query_lower, na=False) |
        df["overview"].str.lower().str.contains(query_lower, na=False) |
        df["genres"].astype(str).str.lower().str.contains(query_lower, na=False)
    ]

    # --- Smart Semantic Search Strategy ---
    semantic_results = pd.DataFrame()
    query_words = payload.query.split()
    
    # Only use semantic search for complex queries or when keyword search is insufficient
    should_use_semantic = (
        len(keyword_results) < 8 and  # Few keyword matches
        (len(query_words) > 1 or      # Multi-word query
         any(len(word) > 8 for word in query_words))  # Complex/descriptive words
    )
    
    if should_use_semantic:
        # Use cached embedding function to avoid recomputation
        query_embedding = get_query_embedding(payload.query)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # FAISS search - much faster than computing all similarities
        _, index_instance = get_ml_components()
        scores, indices = index_instance.search(query_embedding, 12)  # Get top 12 semantic matches
        semantic_results = df.iloc[indices[0]]

    # --- Combine Results ---
    if not semantic_results.empty:
        combined = pd.concat([keyword_results, semantic_results]).drop_duplicates(subset="id")
    else:
        combined = keyword_results

    # --- Early Filter Application (before expensive operations) ---
    if genre_lower:
        combined = combined[combined["genres"].astype(str).str.lower().str.contains(genre_lower, na=False)]
    if payload.language:
        combined = combined[combined["original_language"].astype(str) == payload.language]
    
    # --- Date filtering with optimized parsing ---
    if payload.year_start or payload.year_end:
        # Pre-filter non-null dates first
        combined = combined[combined["release_date"].notnull()]
        if not combined.empty:
            combined["release_year"] = pd.to_datetime(combined["release_date"], errors='coerce').dt.year
            if payload.year_start:
                combined = combined[combined["release_year"] >= payload.year_start]
            if payload.year_end:
                combined = combined[combined["release_year"] <= payload.year_end]
    
    if "adult" in combined.columns and payload.adult is not None:
        if not payload.adult:
            combined = combined[combined["adult"] == payload.adult]

    # --- Sort by relevance (vote_count as tie-breaker) ---
    if not combined.empty:
        combined = combined.sort_values("vote_count", ascending=False)

    top_matches = combined.head(8).to_dict(orient="records") if not combined.empty else []
    
    # Log performance metrics
    end_time = time.time()
    search_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
    print(f"Search '{payload.query}' took {search_time}ms - "
          f"Keyword: {len(keyword_results)}, Semantic: {len(semantic_results)}, "
          f"Final: {len(top_matches)}")
    
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
        ],
        "search_time_ms": search_time  # Include timing in response for debugging
    }