# MovieMatch 🎬

A modern movie recommendation system with AI-powered suggestions and swipe-based interactions.

## 🏗️ **Project Structure**

```
movie-match/
├── frontend/          # Next.js React frontend (deployed on Vercel)
│   ├── src/
│   │   ├── app/       # Next.js app router pages
│   │   ├── components/# React components
│   │   ├── services/  # API integration
│   │   ├── styles/    # CSS and styling
│   │   └── types/     # TypeScript definitions
│   ├── public/        # Static assets
│   └── package.json   # Frontend dependencies
│
└── backend/           # FastAPI Python backend (deployed on Hugging Face Spaces)
    ├── src/
    │   ├── swipe_api.py    # Main FastAPI application
    │   ├── r2_config.py    # Data loading configuration
    │   └── sample_data.py  # Sample data generator
    ├── app.py         # Hugging Face Spaces entry point
    ├── Dockerfile     # Container configuration
    └── requirements.txt # Python dependencies
```

## 🚀 **Getting Started**

This project consists of separate frontend and backend services that must be run independently.

### Prerequisites
- **Node.js 18+** and npm
- **Python 3.8+** (3.9+ recommended)
- **Git**

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:3000

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt  # Install Python dependencies
python app.py
```
Access at: http://localhost:8000




## 🔧 **Architecture**

```
Frontend (localhost:3000)  →  Backend API (localhost:8000)
        ↓                           ↓
  Next.js React App      →  FastAPI Python Server
```

**Note:** Both services must be running simultaneously for the application to work properly.

## ✨ **Features**

- **AI-Powered Recommendations**: Uses sentence transformers for semantic similarity
- **Swipe Interface**: Modern Tinder-like UI for movie discovery
- **Real-time Learning**: Adapts to user preferences
- **Smart Filtering**: Filter by genre, year, and preferences
- **Responsive Design**: Works on all devices

## 🛠️ **Tech Stack**

### Frontend
- **Next.js 15** with App Router
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **Radix UI** for components

### Backend
- **FastAPI** for API framework
- **Sentence Transformers** for AI recommendations
- **FAISS** for similarity search
- **Pandas & NumPy** for data processing

## 🚢 **Deployment**

### Local Development
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000

### Production Options
- **Frontend:** Can be deployed on Vercel, Netlify, or similar
- **Backend:** Can be deployed on Hugging Face Spaces, Railway, or similar
- **Data:** Cloudflare R2 (with local fallbacks)

## 📱 **Usage**

1. **Swipe** on movies to indicate preferences
2. **Get recommendations** based on your taste
3. **Search** for specific movies
4. **Filter** by genres and preferences
5. **Track** your liked and saved movies

## 🔗 **API Endpoints**

**Base URL:** http://localhost:8000

- `GET /` - Health check
- `POST /recommend` - Get personalized recommendations
- `POST /search` - Search movies semantically

Visit http://localhost:8000/docs for interactive API documentation.

## 📄 **License**

MIT License - Feel free to use and modify!

### 4. Environment Configuration

**Frontend (.env.local in frontend/ directory):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

**Backend (.env in backend/ directory, optional):**
```env
# Cloudflare R2 Configuration (Optional - for production)
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
R2_ACCESS_KEY_ID=your_access_key_here  
R2_SECRET_ACCESS_KEY=your_secret_key_here
R2_BUCKET_NAME=movie-match-data
```

## 📖 Usage

1. **Start Backend**: `cd backend && python app.py`
2. **Start Frontend**: `cd frontend && npm run dev`
3. **Open** http://localhost:3000 in your browser
4. **Onboarding**: Select a few movies you like to get started  
5. **Discover**: Swipe through AI-recommended movies
6. **Filter**: Use genre, language, and year filters to refine suggestions
7. **Manage**: View and organize your liked/saved movies in "My Lists"

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

**Frontend (in frontend/ directory):**
```bash
npm run dev               # Start Next.js development server
npm run build             # Build for production  
npm run start             # Start production server
npm run lint              # Run ESLint
```

**Backend (in backend/ directory):**
```bash
python app.py             # Start FastAPI development server
# OR for production:
uvicorn src.swipe_api:app --host 0.0.0.0 --port 8000
```

### Frontend Development
- Built with Next.js 15 + App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Hot reload enabled in development
- Component library: Radix UI + shadcn/ui
- **Run with**: `cd frontend && npm run dev`

### Backend Development
- FastAPI with automatic OpenAPI docs
- Auto-reload enabled in development mode
- Access API documentation at http://localhost:8000/docs
- Interactive API testing at http://localhost:8000/redoc
- **Run with**: `cd backend && python app.py`

## Production Deployment

### Cloudflare R2 Setup

For production deployment, use Cloudflare R2 to store your large data files:

1. **Create R2 Bucket**:
   - Go to Cloudflare Dashboard > R2 Object Storage
   - Create a new bucket (e.g., `movie-match-data`)

2. **Generate API Token**:
   - Go to R2 > Manage R2 API tokens
   - Create token with "Object Read & Write" permissions
   - Save the Access Key ID and Secret Access Key

3. **Configure Environment**:
   ```env
   CLOUDFLARE_ACCOUNT_ID=your_account_id
   R2_ACCESS_KEY_ID=your_access_key  
   R2_SECRET_ACCESS_KEY=your_secret_key
   R2_BUCKET_NAME=your-bucket-name
   ```

4. **Upload Data**:
   ```bash
   pip install boto3 python-dotenv
   python upload_to_r2.py upload
   ```

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
npm run start
```

### Backend (Docker)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
COPY app.py .
CMD ["python", "app.py"]
```

## Troubleshooting

### Common Issues

1. **Backend not starting**
   ```bash
   # Make sure you're in the backend directory
   cd backend
   
   # Activate virtual environment
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Verify virtual environment is active (you should see (venv) in prompt)
   which python  # Should show path with /venv/
   
   # Install dependencies if needed
   pip install -r requirements.txt
   
   # Start the backend
   python app.py
   ```

2. **Frontend API connection issues**
   - Ensure backend is running on port 8000
   - Check `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`
   - Try accessing http://localhost:8000/docs directly to verify backend
   - Check browser console for CORS errors

3. **Port conflicts**
   ```bash
   # If port 3000 is busy, frontend will auto-assign next available port
   # If port 8000 is busy, modify the port in backend/app.py:
   # uvicorn.run(app, host="0.0.0.0", port=8001)
   ```

4. **Missing dependencies**
   ```bash
   # Frontend
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   
   # Backend  
   cd backend
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Virtual environment issues**
   ```bash
   # Recreate virtual environment
   cd backend
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **CORS errors in browser**
   - Ensure backend allows frontend origin
   - Check FastAPI CORS middleware configuration
   - Verify frontend is making requests to correct backend URL

### Performance Tips

- **Backend**: Use FAISS IndexIVFFlat for large datasets
- **Frontend**: Implement pagination for movie results
- **API**: Cache user vectors on client side
- **Images**: Use CDN for movie poster images
- **Development**: Keep both services running during development for best experience

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
