#!/bin/bash
set -e

echo "========================================="
echo "RunPod RAG System Setup"
echo "========================================="

# Set up environment variables
export DEBIAN_FRONTEND=noninteractive
export PYTHONUNBUFFERED=1

# Update and install dependencies
echo "[1/6] Installing system dependencies..."
apt-get update && apt-get install -y \
    git \
    wget \
    vim \
    htop \
    tmux \
    && rm -rf /var/lib/apt/lists/*

# Navigate to workspace
cd /workspace
echo "Working directory: $(pwd)"

# Clone repository (if not already present)
if [ ! -d "hvac-llm" ]; then
    echo "[2/6] Cloning repository..."
    git clone https://github.com/freddie5k/hvac-llm.git
    cd hvac-llm
else
    echo "[2/6] Repository already exists, updating..."
    cd hvac-llm
    git pull
fi

# Install Python dependencies
echo "[3/6] Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Download spaCy model
echo "[4/6] Downloading spaCy language model..."
python -m spacy download en_core_web_sm

# Create necessary directories
echo "[5/6] Creating directories..."
mkdir -p data/documents data/vectorstore logs

# Set up environment file
echo "[6/6] Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your HF_TOKEN"
    echo "   Run: nano .env"
    echo ""
fi

echo "========================================="
echo "✅ Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Add your Hugging Face token"
echo "3. (Optional) Upload documents to data/documents/"
echo "4. Start the server: python src/main.py"
echo ""
echo "For interactive chat: python interactive_chat.py"
echo ""
