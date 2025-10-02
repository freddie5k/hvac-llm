FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Set working directory
WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/documents data/vectorstore logs

# Expose port for FastAPI
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/workspace/.cache/huggingface

# Default command (can be overridden)
CMD ["python", "src/main.py"]
