#!/usr/bin/env python3
"""
Test script to verify RAG functionality via API
"""

import requests
import json

BASE_URL = "http://localhost:8080"

def test_rag_query(question, use_rag=True):
    """Test a RAG query"""
    print(f"\n{'='*60}")
    print(f"Mode: {'RAG' if use_rag else 'Direct'}")
    print(f"Question: {question}")
    print(f"{'='*60}")

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": question,
            "use_rag": use_rag
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"\nAnswer: {data['response']}")

        if data.get('sources'):
            print(f"\nSources:")
            for source in data['sources']:
                print(f"  - {source}")

        print(f"\nMode used: {data.get('mode', 'unknown')}")
        print(f"Status: {data.get('status', 'unknown')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_status():
    """Test status endpoint"""
    response = requests.get(f"{BASE_URL}/status")
    if response.status_code == 200:
        print("\nServer Status:")
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Testing RAG System")
    print("=" * 60)

    # Test status
    test_status()

    # Test RAG queries - customize these based on your document
    test_questions = [
        "What is this document about?",
        "What are the main topics covered?",
    ]

    for question in test_questions:
        # Test with RAG
        test_rag_query(question, use_rag=True)

    print("\n" + "=" * 60)
    print("RAG Testing Complete!")
    print("=" * 60)
