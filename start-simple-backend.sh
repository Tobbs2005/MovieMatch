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

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'http://localhost:3001'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/')
def read_root():
    return {'message': 'MovieMatch API is running'}

@app.post('/recommend')
def get_recommendation():
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
def submit_feedback():
    return {'status': 'success', 'message': 'Feedback recorded'}

@app.get('/search')
def search_movies():
    return {
        'movies': [
            {
                'movieId': 13,
                'title': 'Forrest Gump', 
                'genres': 'Drama, Romance',
                'overview': 'A man with a low IQ has accomplished great things in his life and been present during significant historic events.',
                'release_date': '1994-06-23',
                'poster_path': 'https://image.tmdb.org/t/p/w185/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg'
            }
        ]
    }

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
" &

# Wait for server to start
sleep 3
echo "FastAPI server started at http://localhost:8000"
