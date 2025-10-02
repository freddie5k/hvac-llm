#!/usr/bin/env python3
"""
Diagnostic tool to understand RAG retrieval quality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.rag_system.generation.rag_pipeline import RAGPipeline

def test_retrieval(question, k=5):
    """Test what chunks are being retrieved for a question"""
    print(f"\n{'='*80}")
    print(f"Question: {question}")
    print(f"{'='*80}\n")

    # Initialize RAG
    rag = RAGPipeline()
    rag.vector_store.initialize_collection()

    # Get retrieved documents
    retrieved_docs = rag.vector_store.similarity_search(question, k=k)

    print(f"Retrieved {len(retrieved_docs)} chunks:\n")

    for i, doc in enumerate(retrieved_docs, 1):
        score = doc.get('score', 0)
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})

        print(f"--- Chunk {i} (Score: {score:.3f}) ---")
        print(f"Source: {metadata.get('source', 'unknown')}")
        print(f"Chunk ID: {metadata.get('chunk_id', '?')} / {metadata.get('total_chunks', '?')}")
        print(f"\nContent preview ({len(content)} chars):")
        print(content[:500] + "..." if len(content) > 500 else content)
        print(f"\n{'-'*80}\n")

    return retrieved_docs

def test_full_rag(question, k=5):
    """Test the full RAG pipeline with answer generation"""
    print(f"\n{'='*80}")
    print(f"FULL RAG TEST")
    print(f"Question: {question}")
    print(f"{'='*80}\n")

    # Initialize RAG
    rag = RAGPipeline()
    rag.initialize()

    # Run query
    result = rag.query(question, k=k)

    print("ANSWER:")
    print(result['answer'])
    print(f"\nSources: {', '.join(result['sources'])}")
    print(f"\nRetrieved {len(result['retrieved_docs'])} chunks")

if __name__ == "__main__":
    # Test questions about dehumidifier sizing
    questions = [
        "can you size a dehumidifier?",
        "how to calculate dehumidifier capacity?",
        "what formula is used for dehumidifier sizing?",
    ]

    print("RAG DIAGNOSTICS - Retrieval Quality Test")
    print("="*80)

    for q in questions:
        # First, see what's being retrieved
        test_retrieval(q, k=5)

        # Then see the full answer
        # test_full_rag(q, k=5)

        input("\nPress Enter to continue to next question...")

    print("\n" + "="*80)
    print("Diagnostics complete!")
