# RAG System with Llama 3.1 8B Project

## Project Overview
This is a Retrieval-Augmented Generation (RAG) system using Llama 3.1 8B with 4-bit quantization for 8GB GPU memory optimization.

## Quick Start Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Development
```bash
# Run tests
pytest tests/

# Format code
black src/

# Type checking
mypy src/

# Lint code
flake8 src/
```

### Running the System
```bash
# Start the RAG API server
python src/main.py

# Run document ingestion
python src/rag_system/utils/ingest_documents.py --input data/documents/

# Interactive chat
python src/chat.py
```

## Project Structure
```
hvac-llm/
├── src/
│   └── rag_system/
│       ├── models/          # Llama 3.1 model loading and configuration
│       ├── retrieval/       # Vector database and retrieval logic
│       ├── generation/      # RAG pipeline and response generation
│       └── utils/           # Document processing and utilities
├── data/
│   ├── documents/          # Raw documents for ingestion
│   └── vectorstore/        # Processed vector embeddings
├── config/                 # Configuration files
├── tests/                  # Unit and integration tests
└── docs/                   # Documentation
```

## Key Features
- 4-bit quantization for memory efficiency (8GB GPU)
- Document ingestion from PDF, DOCX, and text files
- Vector similarity search with ChromaDB/FAISS
- RESTful API with FastAPI
- Configurable retrieval and generation parameters

## GPU Memory Optimization
The system uses 4-bit quantization (bitsandbytes) to run Llama 3.1 8B on 8GB GPU memory:
- Model loading with `load_in_4bit=True`
- Compute dtype: `torch.float16`
- Quantization type: `nf4`
- Double quantization enabled

## Environment Variables
Create a `.env` file with:
```
MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
VECTOR_DB_PATH=data/vectorstore
MAX_TOKENS=512
TEMPERATURE=0.7
```