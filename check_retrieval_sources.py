#!/usr/bin/env python3
"""
Check which documents are being retrieved for specific queries
Helps verify if new documents are being used
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.rag_system.retrieval.vector_store import VectorStore

def check_query_sources(query, k=8):
    """See which source documents are retrieved for a query"""
    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print(f"{'='*80}\n")

    vs = VectorStore()
    vs.initialize_collection()

    # Search
    results = vs.similarity_search(query, k=k)

    print(f"Retrieved {len(results)} chunks:\n")

    # Group by source
    by_source = {}
    for r in results:
        source = r['metadata'].get('source', 'unknown')
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(r)

    # Show breakdown
    print("[*] RETRIEVAL BREAKDOWN BY SOURCE:")
    print("-" * 80)
    for source, chunks in by_source.items():
        print(f"\n{source}:")
        print(f"  Chunks retrieved: {len(chunks)}")
        avg_score = sum(c['score'] for c in chunks) / len(chunks)
        print(f"  Average relevance: {avg_score:.3f}")
        scores = ', '.join([f"{c['score']:.3f}" for c in chunks])
        print(f"  Scores: {scores}")

    # Show top chunk from each source
    print(f"\n{'='*80}")
    print("TOP CHUNK FROM EACH SOURCE:")
    print("="*80)

    for source, chunks in by_source.items():
        # Sort by score
        chunks.sort(key=lambda x: x['score'], reverse=True)
        top = chunks[0]

        print(f"\n[DOC] {source}")
        print(f"   Score: {top['score']:.3f}")
        print(f"   Chunk: {top['metadata'].get('chunk_id', '?')} / {top['metadata'].get('total_chunks', '?')}")
        print(f"\n   Content preview:")
        content = top['content']
        print(f"   {content[:400]}...")
        print("-" * 80)

def compare_documents():
    """Show statistics about all documents in vector store"""
    print(f"\n{'='*80}")
    print("DOCUMENT STATISTICS")
    print(f"{'='*80}\n")

    vs = VectorStore()
    vs.initialize_collection()

    # Get all documents
    all_docs = vs.collection.get()

    # Count by source
    sources = {}
    for metadata in all_docs['metadatas']:
        source = metadata.get('source', 'unknown')
        if source not in sources:
            sources[source] = {
                'count': 0,
                'chunks': [],
                'total_chars': 0
            }
        sources[source]['count'] += 1
        sources[source]['chunks'].append(metadata.get('chunk_id', 0))

    # Calculate stats
    for i, content in enumerate(all_docs['documents']):
        source = all_docs['metadatas'][i].get('source', 'unknown')
        sources[source]['total_chars'] += len(content)

    # Display
    print("[*] DOCUMENTS IN VECTOR STORE:\n")
    for source, stats in sources.items():
        avg_chunk_size = stats['total_chars'] / stats['count']
        print(f"[FILE] {source}")
        print(f"   Total chunks: {stats['count']}")
        print(f"   Average chunk size: {avg_chunk_size:.0f} characters")
        print(f"   Total content: {stats['total_chars']:,} characters")
        print()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check which sources are being retrieved")
    parser.add_argument('--action', '-a',
                       choices=['query', 'stats'],
                       default='query',
                       help='Check a query or show document stats')
    parser.add_argument('--query', '-q',
                       help='Query to test (for query action)')
    parser.add_argument('--count', '-k',
                       type=int,
                       default=8,
                       help='Number of chunks to retrieve (default: 8)')

    args = parser.parse_args()

    if args.action == 'stats':
        compare_documents()
    elif args.action == 'query':
        if not args.query:
            # Default test queries
            queries = [
                "dehumidifier sizing formula",
                "moisture load per person",
                "room capacity calculation"
            ]
            print("Testing default queries...\n")
            for q in queries:
                check_query_sources(q, args.count)
                print("\n")
        else:
            check_query_sources(args.query, args.count)
