# MovieMatch AI 🎬

A Next.js-powered movie recommendation app with AI-driven suggestions using machine learning and semantic search.

## Features

- **AI-Powered Recommendations**: Uses sentence transformers and FAISS for intelligent movie suggestions
- **Smart Filtering**: Filter by genre, language, and release year
- **Swipe Interface**: Modern Tinder-like UI for discovering movies
- **User Lists**: Track liked, saved, and disliked movies
- **Real-time Learning**: AI learns from your preferences and improves suggestions
- **Concurrent Development**: One command starts both frontend and backend
- **Dark/Light Mode**: Modern theme switching with system preference detection

## Tech Stack

### Frontend
- **Next.js 15** with App Router
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **Radix UI** components
- **Sonner** for notifications

### Backend
- **FastAPI** for API endpoints
- **sentence-transformers** for movie embeddings
- **FAISS** for similarity search
- **Pandas** for data processing
- **NumPy** for numerical operations

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and npm
- **Python 3.8+** (3.9+ recommended)
- **Git**

### 1. Clone the Repository

```bash
git clone <repository-url>
cd movie-match
```

### 2. Install Frontend Dependencies

```bash
npm install
```

### 3. Setup Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (macOS/Linux)
source venv/bin/activate

# On Windows, use:
# venv\Scripts\activate

# Verify virtual environment is active (you should see (venv) in your prompt)
which python  # Should show path with /venv/

# Install Python dependencies
pip install -r requirements.txt
```

> **⚠️ Important**: Make sure your virtual environment is activated before running the development server. You should see `(venv)` in your terminal prompt.

### 4. Environment Configuration

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

### 5. Data Setup (Optional)

For full AI functionality, place your data files in the `src/data/` directory:
- `TMDB_movie_dataset_v11.csv` - Movie dataset
- `movie_embeddings_v11.npy` - Pre-computed movie embeddings

> **Note**: The app will work with sample data if these files are not provided.

### 6. Start Development Server

**🎉 One command to rule them all:**

```bash
# Make sure your virtual environment is activated first!
source venv/bin/activate  # Skip if already activated

# Start both frontend and backend
npm run dev
```

This will start both services concurrently with colored output:
- **🎨 Frontend**: http://localhost:3000 (or 3001 if 3000 is busy)
- **🤖 Backend**: http://localhost:8000
- **📚 API Docs**: http://localhost:8000/docs

That's it! The app will automatically open in your browser and both services will reload when you make changes.

### ✅ Verify Everything Works

After running `npm run dev`, you should see:

1. **Terminal output** showing both services starting:
   ```
   [FRONTEND] ▲ Next.js 15.4.5
   [FRONTEND] - Local:        http://localhost:3000
   [BACKEND] Starting MovieMatch AI Backend...
   [BACKEND] INFO: Uvicorn running on http://0.0.0.0:8000
   ```

2. **Browser** automatically opens to http://localhost:3000

3. **API accessible** at http://localhost:8000/docs

4. **App functionality**:
   - Click through the intro screen
   - Select movies during onboarding
   - See AI-powered recommendations
   - Use swipe controls or buttons

If any step fails, check the [Troubleshooting](#troubleshooting) section below.

### Alternative: Run Services Separately

If you prefer to run services in separate terminals:

```bash
# Terminal 1: Frontend only
npm run frontend:only

# Terminal 2: Backend only (with venv activated)
source venv/bin/activate
npm run backend:only
```

## 📖 Usage

1. **Open** http://localhost:3000 in your browser
2. **Onboarding**: Select a few movies you like to get started  
3. **Discover**: Swipe through AI-recommended movies
4. **Filter**: Use genre, language, and year filters to refine suggestions
5. **Manage**: View and organize your liked/saved movies in "My Lists"

## API Endpoints

### GET /recommend
Get personalized movie recommendations
```json
{
  "user_vector": [0.1, 0.2, ...],
  "seen_ids": [1, 2, 3],
  "liked_ids": [4, 5],
  "genre": "Action",
  "language": "en",
  "year_start": 2020,
  "year_end": 2024
}
```

### POST /feedback
Submit user feedback for learning
```json
{
  "user_vector": [0.1, 0.2, ...],
  "movie_id": 123,
  "feedback": "like"
}
```

### POST /search
Hybrid search (keyword + semantic)
```json
{
  "query": "space adventure",
  "genre": "Sci-Fi",
  "language": "en"
}
```

## Key Components

### Frontend
- `MovieMatchApp.tsx` - Main application logic
- `MovieCard.tsx` - Individual movie display
- `IntroScreen.tsx` - Onboarding experience
- `Filters.tsx` - Search and filter controls
- `MovieLists.tsx` - User's saved movies

### Backend
- `swipe_api.py` - FastAPI server with ML endpoints
- Movie embeddings using sentence-transformers
- FAISS vector similarity search
- Intelligent recommendation algorithm

## Development

### Available Scripts

```bash
# Development (runs both frontend and backend)
npm run dev                 # Start both services with concurrency
npm run frontend:only       # Start only Next.js frontend
npm run backend:only        # Start only FastAPI backend (requires active venv)

# Production
npm run build              # Build Next.js for production  
npm run start              # Start production Next.js server
npm run lint               # Run ESLint on frontend code
```

### Frontend Development
- Built with Next.js 15 + App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Hot reload enabled in development
- Component library: Radix UI + shadcn/ui

### Backend Development
- FastAPI with automatic OpenAPI docs
- Auto-reload enabled with `--reload` flag
- Access API documentation at http://localhost:8000/docs
- Interactive API testing at http://localhost:8000/redoc

### Development Workflow

1. **Always activate virtual environment first**:
   ```bash
   source venv/bin/activate
   ```

2. **Start development**:
   ```bash
   npm run dev  # Starts both services
   ```

3. **Make changes**:
   - Frontend changes auto-reload in browser
   - Backend changes auto-reload with uvicorn `--reload`
   - Type errors show in terminal and VS Code

4. **Test API endpoints**:
   - Visit http://localhost:8000/docs for interactive testing
   - Use browser dev tools Network tab to inspect requests

## Production Deployment

### Frontend (Vercel/Netlify)
```bash
npm run build
```

### Backend (Docker)
```dockerfile
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.swipe_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Common Issues

1. **Virtual Environment Not Activated**
   ```bash
   # You should see (venv) in your terminal prompt
   # If not, activate it:
   source venv/bin/activate
   
   # Verify it's working:
   which python  # Should show path with /venv/
   which pip     # Should show path with /venv/
   ```

2. **Backend API not accessible**
   - Ensure virtual environment is activated
   - Ensure backend is running on port 8000
   - Check `NEXT_PUBLIC_API_URL` in `.env.local`
   - Try accessing http://localhost:8000/docs directly

3. **Missing movie data**
   - App works with sample data if CSV files are missing
   - For full AI functionality, verify CSV and embedding files are in `src/data/`
   - Check file paths in `swipe_api.py`

4. **Python dependency issues**
   ```bash
   # Recreate virtual environment if needed
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Port conflicts**
   ```bash
   # Frontend: Change port in package.json dev script
   "dev:frontend": "next dev -p 3001"
   
   # Backend: Change port in start-backend-dev.sh
   uvicorn swipe_api:app --reload --port 8001
   ```

6. **Memory issues with embeddings**
   - Consider using FAISS with disk storage
   - Reduce embedding dimensions if needed
   - Monitor memory usage during development

### Performance Tips

- Use FAISS IndexIVFFlat for large datasets
- Implement pagination for movie results
- Cache user vectors on client side
- Use CDN for movie poster images
- Keep virtual environment activated throughout development session

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- TMDB for movie data
- Sentence Transformers for embeddings
- The open-source community for amazing tools

---

**MovieMatch AI** - Discover your next favorite movie with the power of AI! 🎬✨

*Built with ❤️ using Next.js, FastAPI, and machine learning.*
