# MovieMatch Backend - Hugging Face Spaces Deployment Guide

## 🎯 Quick Start

Your MovieMatch backend is now ready for Hugging Face Spaces deployment! Here's everything you need:

## 📁 Required Files (All Ready!)

✅ **Core Application Files:**
- `app.py` - Main entry point for Hugging Face Spaces
- `requirements_hf.txt` - Optimized dependencies for Spaces
- `Dockerfile` - Container configuration
- `deploy_to_spaces.sh` - Deployment helper script

✅ **Source Code:**
- `src/swipe_api.py` - Main FastAPI application
- `src/r2_config.py` - Data loading with fallbacks
- `src/sample_data.py` - Sample data generator for testing

✅ **Documentation:**
- `README_SPACES.md` - Comprehensive documentation
- This deployment guide

## 🚀 Deployment Steps

### 1. Create Hugging Face Space

1. Go to [https://huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Configure your space:
   - **Name:** `moviematch-backend` (or your preferred name)
   - **SDK:** `Docker`
   - **Hardware:** `CPU basic` (free tier works!)
   - **Visibility:** Public or Private (your choice)

### 2. Configure Space Metadata

Add this to the top of your Space's README.md:

```yaml
---
title: MovieMatch AI Backend
emoji: 🎬
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---
```

### 3. Upload Files

Upload these files to your Space:

**Required:**
- `app.py`
- `requirements_hf.txt` (rename to `requirements.txt`)
- `Dockerfile`
- `src/` directory (entire folder)

**Optional:**
- `README_SPACES.md` (for documentation)

### 4. Environment Variables (Optional)

If you want to use Cloudflare R2 for data storage, add these secrets in your Space settings:

- `CLOUDFLARE_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID` 
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`

*If not set, the app will use sample data for testing.*

## 🔧 How It Works

The app has intelligent fallback mechanisms:

1. **First:** Tries to load from Cloudflare R2 (if configured)
2. **Second:** Falls back to local data files (if available)
3. **Third:** Generates sample movie data for testing

This ensures your app always works, even without the full dataset!

## 📊 Memory Optimization

The backend is optimized for Hugging Face Spaces:
- Memory usage < 512MB
- Efficient data loading
- Lazy loading of ML components
- CPU-only inference

## 🧪 Testing

Once deployed, test these endpoints:

- `GET /` - Health check
- `GET /health` - Detailed status
- `POST /recommend` - Get recommendations
- `POST /search` - Search movies
- `GET /movies/random` - Random movies

## 🎬 API Example

```bash
# Test your deployed Space
curl -X POST "https://your-username-moviematch-backend.hf.space/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "seen_ids": [1, 2, 3],
    "liked_ids": [1, 3],
    "genre": "Action"
  }'
```

## 🔗 Frontend Integration

Your frontend can connect to the Space URL:
```
https://your-username-moviematch-backend.hf.space
```

## 🎉 You're Ready!

Everything is configured and optimized for Hugging Face Spaces. The deployment should work smoothly with automatic fallbacks ensuring reliability.

**Happy deploying! 🚀**
