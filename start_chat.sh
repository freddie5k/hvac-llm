#!/bin/bash
# Simple startup script for interactive chat on RunPod

set -e

echo "Starting RAG System Interactive Chat..."

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

# Start interactive chat
echo "Loading model and starting chat interface..."
$PYTHON_CMD src/chat.py
