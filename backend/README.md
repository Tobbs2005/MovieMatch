---
title: MovieMatch Backend
emoji: 🎬
colorFrom: red
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# MovieMatch AI Backend 🎬

A FastAPI backend for personalized movie recommendations using AI and swipe-based interactions.

## Features

- **Smart Recommendations**: Uses sentence transformers for semantic similarity
- **Swipe Interface**: Tracks user likes/dislikes for personalized suggestions  
- **Memory Optimized**: Runs efficiently within Spaces limits
- **Real Movie Database**: Uses authentic TMDB movie data and embeddings
- **JSON API**: RESTful endpoints for frontend integration
- **Production Ready**: Requires real data, no sample/dummy content

## API Endpoints

- `GET /` - Health check
- `POST /recommend` - Get movie recommendations
- `POST /search` - Search movies semantically
- `GET /health` - Detailed health status

## Usage

```bash
# Get a movie recommendation
curl -X POST https://tobbs2005-movie-match.hf.space/recommend \
  -H "Content-Type: application/json" \
  -d '{"seen_ids": [1,2,3], "liked_ids": [1,3], "genre": "Action"}'
```

Built with FastAPI, Sentence Transformers, and FAISS for fast similarity search.
