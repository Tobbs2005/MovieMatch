# Cloudflare R2 Setup Guide

## 🚀 Quick Start

### 1. Create Cloudflare R2 Bucket

1. **Log into Cloudflare Dashboard**
2. **Go to R2 Object Storage** in the left sidebar
3. **Create Bucket**:
   - Click "Create bucket"
   - Name: `movie-match-data` (or your preferred name)
   - Location: Choose closest to your users
   - Click "Create bucket"

### 2. Generate R2 API Token

1. **In R2 Dashboard**, click "Manage R2 API tokens"
2. **Create API token**:
   - Token name: `movie-match-api`
   - Permissions: `Object Read & Write`
   - Specify bucket: Select your bucket or leave for all buckets
   - TTL: Set expiration or leave blank for no expiration
3. **Save credentials**:
   - Copy the **Access Key ID**
   - Copy the **Secret Access Key**
   - Note your **Account ID** (shown in dashboard sidebar)

### 3. Configure Environment Variables

Create or update your `.env.local` file:

```bash
# Next.js Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development

# Cloudflare R2 Configuration
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
R2_ACCESS_KEY_ID=your_access_key_here
R2_SECRET_ACCESS_KEY=your_secret_key_here
R2_BUCKET_NAME=movie-match-data
```

### 4. Upload Data to R2

```bash
# Install dependencies
pip install boto3 python-dotenv

# Upload your local data files
python upload_to_r2.py upload

# Verify upload
python upload_to_r2.py list
```

## 📊 What Gets Uploaded

- **TMDB_movie_dataset_v11.csv** (~200MB) - Movie metadata
- **movie_embeddings_v11.npy** (~1.9GB) - Pre-computed embeddings

## 💰 R2 Costs

Cloudflare R2 pricing (as of 2024):
- **Storage**: $0.015/GB/month (~$0.03/month for this app)
- **Operations**: Very low cost for API calls
- **Egress**: FREE (unlike AWS S3)
- **First 10GB**: FREE storage

## 🔄 How It Works

1. **Production**: Loads data from R2 bucket
2. **Development**: Falls back to local files if R2 not configured
3. **Caching**: Downloads and caches files locally for faster access
4. **Automatic**: No code changes needed between environments

## 🛠️ Troubleshooting

### "Missing R2 credentials" Error
- Check your `.env.local` file has all required variables
- Verify credentials are correct in Cloudflare dashboard
- Make sure Account ID is from the right sidebar

### "Access Denied" Error
- Verify API token has "Object Read & Write" permissions
- Check if token is restricted to specific bucket
- Ensure bucket name matches `R2_BUCKET_NAME`

### "Bucket not found" Error
- Verify bucket name spelling in environment variables
- Check bucket exists in your Cloudflare account
- Ensure you're using the correct Account ID

## 🚀 Production Deployment

For production (Vercel, Railway, etc.), add these environment variables:

```bash
CLOUDFLARE_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=movie-match-data
```

The app will automatically use R2 in production and fall back to local files in development!
