#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from src.rag_system.generation.rag_pipeline import RAGPipeline
from src.rag_system.utils.document_processor import DocumentProcessor

def main():
    parser = argparse.ArgumentParser(description="Ingest documents into the RAG system")
    parser.add_argument("--input", "-i", required=True, help="Input directory containing documents")
    parser.add_argument("--chunk-size", "-c", type=int, default=1000, help="Chunk size for text splitting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input directory '{input_path}' does not exist")
        return 1
    
    if not input_path.is_dir():
        print(f"Error: '{input_path}' is not a directory")
        return 1
    
    print("Initializing RAG system...")
    rag_pipeline = RAGPipeline()
    document_processor = DocumentProcessor()
    
    try:
        rag_pipeline.initialize()
        print("[OK] RAG system initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize RAG system: {e}")
        return 1
    
    print(f"\n[*] Processing documents from: {input_path}")

    try:
        documents = document_processor.process_directory(str(input_path), chunk_size=args.chunk_size)

        if not documents:
            print("[WARNING] No supported documents found in the directory")
            return 0

        print(f"[*] Found {len(documents)} document chunks")

        # Prepare data for vector store
        texts = [doc['content'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        ids = [f"{doc['metadata']['source']}_{doc['metadata']['chunk_id']}" for doc in documents]

        print("[*] Adding documents to vector store...")
        rag_pipeline.add_documents(texts, metadatas, ids)

        print("[OK] Documents successfully ingested!")

        if args.verbose:
            print("\nProcessed files:")
            sources = set(doc['metadata']['source'] for doc in documents)
            for source in sorted(sources):
                chunks = sum(1 for doc in documents if doc['metadata']['source'] == source)
                print(f"  - {source}: {chunks} chunks")

        return 0

    except Exception as e:
        print(f"[ERROR] Error during document ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())