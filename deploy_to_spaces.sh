#!/bin/bash

# MovieMatch Backend - Hugging Face Spaces Deployment Script
echo "🎬 MovieMatch Backend - Hugging Face Spaces Setup"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "📋 Pre-deployment checklist:"
echo ""

# 1. Check required files
echo "✅ Checking required files..."
REQUIRED_FILES=("app.py" "requirements_hf.txt" "src/swipe_api.py" "src/r2_config.py" "src/sample_data.py")
MISSING_FILES=()

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo "  ✅ All required files present"
else
    echo "  ❌ Missing files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "     - $file"
    done
fi

# 2. Check dependencies
echo ""
echo "✅ Checking Python dependencies..."
if python3 -c "import fastapi, uvicorn, pandas, numpy" 2>/dev/null; then
    echo "  ✅ Core dependencies available"
else
    echo "  ⚠️  Some dependencies missing (will be installed on Spaces)"
fi

# 3. Test basic import
echo ""
echo "✅ Testing basic imports..."
cd src
if python3 -c "from sample_data import generate_sample_movies; print('Sample data generator works')" 2>/dev/null; then
    echo "  ✅ Sample data generator works"
else
    echo "  ❌ Sample data generator has issues"
fi
cd ..

# 4. Show next steps
echo ""
echo "🚀 Next steps for Hugging Face Spaces deployment:"
echo ""
echo "1. Create a new Space on Hugging Face Hub:"
echo "   - Go to https://huggingface.co/spaces"
echo "   - Click 'Create new Space'"
echo "   - Choose 'Docker' as SDK"
echo "   - Set app_port to 7860"
echo ""
echo "2. Upload these files to your Space:"
echo "   - app.py (main entry point)"
echo "   - requirements_hf.txt (rename to requirements.txt)"
echo "   - Dockerfile"
echo "   - src/ directory (entire folder)"
echo "   - README_SPACES.md (optional documentation)"
echo ""
echo "3. Optional: Set environment variables if using R2:"
echo "   - CLOUDFLARE_ACCOUNT_ID"
echo "   - R2_ACCESS_KEY_ID"
echo "   - R2_SECRET_ACCESS_KEY"
echo "   - R2_BUCKET_NAME"
echo ""
echo "4. The app will automatically:"
echo "   - Try to load from R2 (if configured)"
echo "   - Fall back to local data files (if available)"
echo "   - Generate sample data for testing (if no data available)"
echo ""
echo "📝 Your Space configuration should include:"
echo "---"
echo "title: MovieMatch AI Backend"
echo "emoji: 🎬"
echo "colorFrom: blue"
echo "colorTo: purple"
echo "sdk: docker"
echo "pinned: false"
echo "license: mit"
echo "app_port: 7860"
echo "---"
echo ""
echo "✨ Ready for deployment!"
