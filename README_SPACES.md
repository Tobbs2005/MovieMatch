# MovieMatch AI Backend - Hugging Face Spaces

This is the backend API for MovieMatch, a movie recommendation application that uses AI to provide personalized movie suggestions based on user preferences and behavior.

## 🎬 Features

- **Smart Recommendations**: Uses sentence transformers and FAISS for semantic similarity matching
- **Memory Optimized**: Designed to run efficiently within Hugging Face Spaces memory limits
- **Swipe Interface Support**: Tracks user likes/dislikes for improved recommendations
- **Genre Filtering**: Filter recommendations by movie genres
- **Search Functionality**: Semantic search across movie database
- **Real-time Learning**: Adapts recommendations based on user feedback

## 🚀 Deployment on Hugging Face Spaces

### Prerequisites

1. Create a new Space on Hugging Face Hub
2. Choose **Gradio** as the SDK (even though we're using FastAPI)
3. Set the Space to **Public** or **Private** as needed

### Setup Steps

1. **Clone this repository** to your Hugging Face Space
2. **Configure Environment Variables** (if using external data sources):
   - `CLOUDFLARE_ACCOUNT_ID`: Your Cloudflare account ID (optional)
   - `R2_ACCESS_KEY_ID`: R2 access key (optional)
   - `R2_SECRET_ACCESS_KEY`: R2 secret key (optional)
   - `R2_BUCKET_NAME`: R2 bucket name (optional)

3. **Upload Data Files** (if not using R2):
   - Place `TMDB_movie_dataset_v11.csv` in `src/data/`
   - Place `movie_embeddings_v11.npy` in `src/data/`

### File Structure

```
├── app.py                 # Main entry point for Hugging Face Spaces
├── requirements.txt       # Python dependencies
├── src/
│   ├── swipe_api.py      # Main FastAPI application
│   ├── r2_config.py      # Data loading from R2 or local files
│   └── data/             # Local data files (if not using R2)
│       ├── TMDB_movie_dataset_v11.csv
│       └── movie_embeddings_v11.npy
```

## 📱 API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health status

### Core Features
- `POST /recommend` - Get movie recommendations
- `POST /search` - Search movies semantically
- `GET /movies/random` - Get random movies for initial swipe deck
- `GET /genres` - Get list of available genres

### Request Examples

#### Get Recommendations
```json
POST /recommend
{
  "seen_ids": [1, 2, 3],
  "liked_ids": [1, 3],
  "genre": "Action"
}
```

#### Search Movies
```json
POST /search
{
  "query": "space adventure with robots",
  "genre": "Sci-Fi"
}
```

## 🔧 Configuration

The application automatically detects the environment and configures itself accordingly:

- **Memory Optimization**: Reduces dataset size and uses efficient data types
- **Lazy Loading**: ML components are loaded only when needed
- **Fallback Data Loading**: Tries R2 first, falls back to local files
- **CPU-Only Inference**: Uses CPU for compatibility with Hugging Face Spaces

## 🏗️ Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **Sentence Transformers**: For generating movie embeddings
- **FAISS**: For fast similarity search
- **Pandas & NumPy**: For data manipulation
- **Cloudflare R2**: Optional cloud storage for datasets

## 📊 Performance

Optimized for Hugging Face Spaces constraints:
- Memory usage < 512MB
- Fast startup time
- Efficient similarity search
- Minimal dependencies

## 🔗 Integration

This backend is designed to work with the MovieMatch frontend. The frontend can be deployed separately and configured to call this API.

Frontend repository: [Add your frontend repo URL here]

## 📝 License

[Add your license information here]

## 🤝 Contributing

[Add contributing guidelines here]
