#!/usr/bin/env python3
"""
Test the final improved RAG system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.rag_system.generation.rag_pipeline import RAGPipeline

def test_final(question):
    """Test with the improved settings"""
    print(f"\n{'='*80}")
    print(f"FINAL TEST - Improved RAG System")
    print(f"Question: {question}")
    print(f"{'='*80}\n")

    # Initialize RAG
    rag = RAGPipeline()
    rag.initialize()

    # Override max_tokens to 1024
    rag.max_tokens = 1024

    # Run query
    result = rag.query(question, k=8)

    print("="*80)
    print("ANSWER:")
    print("="*80)
    print(result['answer'])
    print(f"\n{'='*80}")
    print(f"Sources: {', '.join(result['sources'])}")
    print(f"Retrieved {len(result['retrieved_docs'])} chunks")
    print(f"Answer length: {len(result['answer'])} characters")

if __name__ == "__main__":
    # Test the specific question
    question = "can you size a dehumidifier for a 50 square meter room with 4 people to reach 30% RH?"
    test_final(question)
