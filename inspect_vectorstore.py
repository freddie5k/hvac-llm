#!/usr/bin/env python3
"""
Inspect what's stored in the local vector database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.rag_system.retrieval.vector_store import VectorStore

def inspect_collection():
    """Show what's in the vector store"""
    print("="*80)
    print("VECTOR STORE INSPECTION")
    print("="*80)

    vs = VectorStore()
    vs.initialize_collection()

    # Get collection info
    collection = vs.collection
    count = collection.count()

    print(f"\n📊 Collection Statistics:")
    print(f"   Total chunks: {count}")
    print(f"   Location: {vs.persist_directory}")
    print(f"   Collection name: {vs.collection_name}")

    if count == 0:
        print("\n⚠️  Vector store is empty!")
        return

    # Get all documents
    print(f"\n📄 Retrieving all {count} chunks...")
    results = collection.get()

    # Analyze sources
    sources = {}
    for metadata in results['metadatas']:
        source = metadata.get('source', 'unknown')
        if source not in sources:
            sources[source] = 0
        sources[source] += 1

    print(f"\n📁 Documents in vector store:")
    for source, chunk_count in sources.items():
        print(f"   - {source}: {chunk_count} chunks")

    # Show sample chunks
    print(f"\n📋 Sample Chunks (showing first 5):\n")
    for i in range(min(5, len(results['documents']))):
        doc_id = results['ids'][i]
        content = results['documents'][i]
        metadata = results['metadatas'][i]

        print(f"--- Chunk {i+1} ---")
        print(f"ID: {doc_id}")
        print(f"Source: {metadata.get('source', 'unknown')}")
        print(f"Chunk: {metadata.get('chunk_id', '?')} / {metadata.get('total_chunks', '?')}")
        print(f"Length: {len(content)} characters")
        print(f"\nContent preview:")
        print(content[:300] + "..." if len(content) > 300 else content)
        print("\n" + "="*80 + "\n")

def search_in_vectorstore(query, k=5):
    """Search the vector store and show what would be retrieved"""
    print("="*80)
    print(f"SEARCH QUERY: {query}")
    print("="*80)

    vs = VectorStore()
    vs.initialize_collection()

    results = vs.similarity_search(query, k=k)

    print(f"\nFound {len(results)} matching chunks:\n")

    for i, doc in enumerate(results, 1):
        score = doc.get('score', 0)
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})

        print(f"--- Match {i} (Relevance: {score:.3f}) ---")
        print(f"Source: {metadata.get('source', 'unknown')}")
        print(f"Chunk: {metadata.get('chunk_id', '?')} / {metadata.get('total_chunks', '?')}")
        print(f"\nContent ({len(content)} chars):")
        print(content)
        print("\n" + "="*80 + "\n")

def export_to_text():
    """Export all chunks to a text file for review"""
    vs = VectorStore()
    vs.initialize_collection()

    results = vs.collection.get()

    output_file = "vectorstore_export.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("COMPLETE VECTOR STORE EXPORT\n")
        f.write("="*80 + "\n\n")

        for i in range(len(results['documents'])):
            doc_id = results['ids'][i]
            content = results['documents'][i]
            metadata = results['metadatas'][i]

            f.write(f"--- Chunk {i+1}/{len(results['documents'])} ---\n")
            f.write(f"ID: {doc_id}\n")
            f.write(f"Source: {metadata.get('source', 'unknown')}\n")
            f.write(f"Chunk: {metadata.get('chunk_id', '?')} / {metadata.get('total_chunks', '?')}\n")
            f.write(f"Length: {len(content)} characters\n\n")
            f.write("Content:\n")
            f.write(content)
            f.write("\n\n" + "="*80 + "\n\n")

    print(f"✅ Exported all chunks to: {output_file}")
    print(f"   Total chunks: {len(results['documents'])}")
    print(f"   You can open this file to review everything stored locally")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Inspect local vector store")
    parser.add_argument('--action', '-a',
                       choices=['inspect', 'search', 'export'],
                       default='inspect',
                       help='What to do: inspect stats, search, or export all')
    parser.add_argument('--query', '-q',
                       help='Search query (for search action)')
    parser.add_argument('--count', '-k',
                       type=int,
                       default=5,
                       help='Number of results for search (default: 5)')

    args = parser.parse_args()

    if args.action == 'inspect':
        inspect_collection()
    elif args.action == 'search':
        if not args.query:
            print("Error: --query required for search action")
            print("Example: python inspect_vectorstore.py --action search --query 'dehumidifier sizing'")
        else:
            search_in_vectorstore(args.query, args.count)
    elif args.action == 'export':
        export_to_text()
