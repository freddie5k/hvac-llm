#!/bin/bash
set -e

echo "========================================="
echo "RunPod RAG System Setup"
echo "========================================="

# Set up environment variables
export DEBIAN_FRONTEND=noninteractive
export PYTHONUNBUFFERED=1

# Update and install dependencies
echo "[1/7] Installing system dependencies..."
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
    echo "[2/7] Cloning repository..."
    git clone https://github.com/freddie5k/hvac-llm.git
    cd hvac-llm
else
    echo "[2/7] Repository already exists, updating..."
    cd hvac-llm
    git pull
fi

# Detect Python version and set up consistent environment
echo "[3/7] Detecting Python environment..."
PYTHON_CMD=$(which python3 || which python)
echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Install Python dependencies using the detected Python
echo "[4/7] Installing Python dependencies..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install --no-cache-dir -r requirements.txt

# Download spaCy model
echo "[5/7] Downloading spaCy language model..."
$PYTHON_CMD -m spacy download en_core_web_sm

# Create necessary directories
echo "[6/7] Creating directories..."
mkdir -p data/documents data/vectorstore logs

# Set up environment file and PYTHONPATH
echo "[7/7] Setting up environment variables..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your HF_TOKEN"
    echo "   Run: nano .env"
    echo ""
fi

# Add PYTHONPATH to bashrc for persistent use
if ! grep -q "PYTHONPATH=/workspace/hvac-llm/src" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# RAG System Python path" >> ~/.bashrc
    echo "export PYTHONPATH=/workspace/hvac-llm/src:\$PYTHONPATH" >> ~/.bashrc
fi

# Set PYTHONPATH for current session
export PYTHONPATH=/workspace/hvac-llm/src:$PYTHONPATH

echo "========================================="
echo "✅ Setup complete!"
echo "========================================="
echo ""
echo "Python environment:"
echo "  Python: $PYTHON_CMD ($($PYTHON_CMD --version))"
echo "  PYTHONPATH: $PYTHONPATH"
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Add your Hugging Face token (HF_TOKEN=...)"
echo "3. (Optional) Upload documents to data/documents/"
echo "4. Start the server:"
echo "   cd /workspace/hvac-llm/src"
echo "   $PYTHON_CMD main.py"
echo ""
echo "For interactive chat:"
echo "   cd /workspace/hvac-llm"
echo "   $PYTHON_CMD interactive_chat.py"
echo ""
