#!/bin/bash

echo "Starting Simple FastAPI Backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install basic dependencies first
echo "Installing basic dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn

echo "Starting FastAPI server on http://localhost:8000"
cd src && python -c "
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://localhost:3001'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Request/Response models
class RecommendRequest(BaseModel):
    user_vector: Optional[List[float]] = None
    seen_ids: List[int]
    liked_ids: List[int]
    genre: Optional[str] = None
    language: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    adult: Optional[bool] = None

class SearchRequest(BaseModel):
    query: str
    genre: Optional[str] = None
    language: Optional[str] = None
    year_start: Optional[int] = None
    year_end: Optional[int] = None
    adult: Optional[bool] = None

class FeedbackRequest(BaseModel):
    movie_id: int
    liked: bool
    user_vector: Optional[List[float]] = None

@app.get('/')
def read_root():
    return {'message': 'MovieMatch API is running'}

@app.post('/recommend')
def get_recommendation(request: RecommendRequest):
    return {
        'movie': {
            'movieId': 550,
            'title': 'Fight Club',
            'genres': 'Drama',
            'overview': 'A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy.',
            'release_date': '1999-10-15',
            'poster_path': 'https://image.tmdb.org/t/p/w185/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg'
        },
        'user_vector': None
    }

@app.post('/feedback')
def submit_feedback(request: FeedbackRequest):
    return {'status': 'success', 'message': 'Feedback recorded'}

@app.post('/search')
def search_movies(request: SearchRequest):
    return {
        'movies': [
            {
                'movieId': 13,
                'title': 'Forrest Gump', 
                'genres': 'Drama, Romance',
                'overview': 'A man with a low IQ has accomplished great things in his life and been present during significant historic events.',
                'release_date': '1994-06-23',
                'poster_path': 'https://image.tmdb.org/t/p/w185/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg'
            },
            {
                'movieId': 680,
                'title': 'Pulp Fiction',
                'genres': 'Crime, Drama',
                'overview': 'A burger-loving hit man, his philosophical partner, and a drug-addicted boxer are caught up in a web of crime.',
                'release_date': '1994-09-10',
                'poster_path': 'https://image.tmdb.org/t/p/w185/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg'
            }
        ]
    }

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
" &

# Wait for server to start
sleep 3
echo "FastAPI server started at http://localhost:8000"
