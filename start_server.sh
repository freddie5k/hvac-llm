#!/bin/bash
# Simple startup script for RunPod deployment

set -e

echo "Starting RAG System Server..."

# Detect Python
PYTHON_CMD=$(which python3 2>/dev/null || which python)
echo "Using Python: $PYTHON_CMD"

# Set PYTHONPATH
export PYTHONPATH=/workspace/hvac-llm/src:$PYTHONPATH

# Navigate to project directory
cd /workspace/hvac-llm

# Check for .env file
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with your HF_TOKEN"
    echo "Example:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Check for HF_TOKEN
if ! grep -q "HF_TOKEN=hf_" .env; then
    echo "WARNING: HF_TOKEN not configured in .env file"
    echo "Please edit .env and add your Hugging Face token"
    echo "Get your token from: https://huggingface.co/settings/tokens"
fi

# Start the server
echo "Starting FastAPI server on port 8000..."
cd src
$PYTHON_CMD main.py
