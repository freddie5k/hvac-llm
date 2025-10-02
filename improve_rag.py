#!/usr/bin/env python3
"""
Script to re-ingest documents with better chunk size and test improvements
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.rag_system.generation.rag_pipeline import RAGPipeline
from src.rag_system.utils.document_processor import DocumentProcessor
from pathlib import Path

def reingest_with_better_chunks(chunk_size=1500, overlap=300):
    """Re-ingest documents with larger, better overlapping chunks"""
    print(f"\n{'='*80}")
    print(f"Re-ingesting documents with improved settings:")
    print(f"  - Chunk size: {chunk_size} characters")
    print(f"  - Overlap: {overlap} characters")
    print(f"{'='*80}\n")

    # Initialize
    rag_pipeline = RAGPipeline()
    document_processor = DocumentProcessor()

    # Delete old collection
    print("[*] Deleting old vector store...")
    try:
        rag_pipeline.vector_store.delete_collection()
    except:
        pass

    # Re-initialize
    print("[*] Initializing new vector store...")
    rag_pipeline.vector_store.initialize_collection()

    # Process documents with new chunk size
    input_path = Path("data/documents")
    print(f"[*] Processing documents from: {input_path}")

    documents = document_processor.process_directory(
        str(input_path),
        chunk_size=chunk_size
    )

    print(f"[*] Found {len(documents)} chunks (was 291 with size 800)")

    # Add to vector store
    texts = [doc['content'] for doc in documents]
    metadatas = [doc['metadata'] for doc in documents]
    ids = [f"{doc['metadata']['source']}_{doc['metadata']['chunk_id']}" for doc in documents]

    print("[*] Adding documents to vector store...")
    rag_pipeline.add_documents(texts, metadatas, ids)

    print("[OK] Re-ingestion complete!")
    print(f"\nNew chunk count: {len(documents)}")
    print(f"Average chunk size: {sum(len(t) for t in texts) / len(texts):.0f} chars")

    return len(documents)

def test_improved_retrieval(question, k=8):
    """Test with more chunks retrieved"""
    print(f"\n{'='*80}")
    print(f"Testing improved retrieval (k={k})")
    print(f"Question: {question}")
    print(f"{'='*80}\n")

    rag = RAGPipeline()
    rag.initialize()

    result = rag.query(question, k=k)

    print("ANSWER:")
    print(result['answer'])
    print(f"\nSources: {', '.join(result['sources'])}")
    print(f"Retrieved {len(result['retrieved_docs'])} chunks")

if __name__ == "__main__":
    print("RAG IMPROVEMENT PROCESS")
    print("="*80)

    # Step 1: Re-ingest with better chunk size
    new_chunk_count = reingest_with_better_chunks(chunk_size=1500, overlap=300)

    print("\n" + "="*80)
    print("TESTING WITH IMPROVED SETTINGS")
    print("="*80)

    # Step 2: Test with more retrieval chunks
    test_questions = [
        "can you size a dehumidifier?",
        "what is the formula for dehumidifier capacity calculation?",
    ]

    for q in test_questions:
        test_improved_retrieval(q, k=8)

    print("\n" + "="*80)
    print("Improvement complete!")
    print("="*80)
