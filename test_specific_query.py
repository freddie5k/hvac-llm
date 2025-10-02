#!/usr/bin/env python3
"""
Test the specific user query to see what's being retrieved
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.rag_system.generation.rag_pipeline import RAGPipeline

def test_query(question):
    """Test what chunks are retrieved for this specific question"""
    print(f"\n{'='*80}")
    print(f"Question: {question}")
    print(f"{'='*80}\n")

    # Initialize RAG
    rag = RAGPipeline()
    rag.vector_store.initialize_collection()

    # Get retrieved documents
    retrieved_docs = rag.vector_store.similarity_search(question, k=8)

    print(f"Retrieved {len(retrieved_docs)} chunks:\n")

    for i, doc in enumerate(retrieved_docs, 1):
        score = doc.get('score', 0)
        content = doc.get('content', '')

        print(f"--- Chunk {i} (Score: {score:.3f}) ---")
        print(f"Length: {len(content)} chars")
        print(f"\nContent:")
        print(content)
        print(f"\n{'-'*80}\n")

if __name__ == "__main__":
    question = "can you size a dehumidifier for a 50 square meter room with 4 people to reach 30% RH?"
    test_query(question)
