#!/usr/bin/env python3
"""
Manage documents in the vector store - add, replace, or test new docs
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from src.rag_system.generation.rag_pipeline import RAGPipeline
from src.rag_system.utils.document_processor import DocumentProcessor
from pathlib import Path

def clear_vectorstore():
    """Delete all documents from vector store"""
    print("\n" + "="*80)
    print("CLEARING VECTOR STORE")
    print("="*80)

    rag = RAGPipeline()

    try:
        rag.vector_store.delete_collection()
        print("\n[OK] Vector store cleared successfully!")
    except Exception as e:
        print(f"\n[NOTE] {e}")

    # Re-initialize empty collection
    rag.vector_store.initialize_collection()
    print("[OK] New empty collection created")

def ingest_documents(input_path, chunk_size=1500):
    """Ingest documents from a specific directory"""
    print("\n" + "="*80)
    print(f"INGESTING DOCUMENTS")
    print(f"Source: {input_path}")
    print(f"Chunk size: {chunk_size}")
    print("="*80)

    # Initialize
    rag = RAGPipeline()
    doc_processor = DocumentProcessor()

    # Initialize vector store (doesn't delete existing)
    rag.vector_store.initialize_collection()

    # Get current count
    current_count = rag.vector_store.collection.count()
    print(f"\n[STATS] Current chunks in vector store: {current_count}")

    # Process documents
    input_path = Path(input_path)

    if not input_path.exists():
        print(f"\n[ERROR] Error: Path '{input_path}' does not exist")
        return

    print(f"\n[DIR] Processing documents from: {input_path}")

    documents = doc_processor.process_directory(
        str(input_path),
        chunk_size=chunk_size
    )

    if not documents:
        print("\n[WARNING]  No documents found to process")
        return

    print(f"[FILE] Found {len(documents)} new chunks to add")

    # Show what files were found
    sources = {}
    for doc in documents:
        source = doc['metadata']['source']
        if source not in sources:
            sources[source] = 0
        sources[source] += 1

    print(f"\n[DOCS] Files to be added:")
    for source, count in sources.items():
        print(f"   - {source}: {count} chunks")

    # Add to vector store
    texts = [doc['content'] for doc in documents]
    metadatas = [doc['metadata'] for doc in documents]
    ids = [f"{doc['metadata']['source']}_{doc['metadata']['chunk_id']}" for doc in documents]

    print(f"\n[SAVE] Adding {len(documents)} chunks to vector store...")
    rag.add_documents(texts, metadatas, ids)

    # Get new count
    new_count = rag.vector_store.collection.count()
    print(f"\n[OK] Success!")
    print(f"   Before: {current_count} chunks")
    print(f"   Added:  {len(documents)} chunks")
    print(f"   Total:  {new_count} chunks")

def show_current_documents():
    """Show what documents are currently in the vector store"""
    print("\n" + "="*80)
    print("CURRENT DOCUMENTS IN VECTOR STORE")
    print("="*80)

    vs = RAGPipeline().vector_store
    vs.initialize_collection()

    results = vs.collection.get()

    if not results['metadatas']:
        print("\n[WARNING]  Vector store is empty")
        return

    sources = {}
    for metadata in results['metadatas']:
        source = metadata.get('source', 'unknown')
        if source not in sources:
            sources[source] = 0
        sources[source] += 1

    print(f"\n[STATS] Total chunks: {len(results['documents'])}")
    print(f"\n[DIR] Documents:")
    for source, count in sources.items():
        print(f"   - {source}: {count} chunks")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage RAG documents")
    parser.add_argument('action',
                       choices=['clear', 'add', 'show', 'replace'],
                       help='Action to perform')
    parser.add_argument('--input', '-i',
                       help='Input directory with documents (for add/replace)')
    parser.add_argument('--chunk-size', '-c',
                       type=int,
                       default=1500,
                       help='Chunk size (default: 1500)')

    args = parser.parse_args()

    if args.action == 'clear':
        confirm = input("[WARNING] This will delete ALL documents from vector store. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            clear_vectorstore()
        else:
            print("[ERROR] Cancelled")

    elif args.action == 'add':
        if not args.input:
            print("[ERROR] Error: --input required for add action")
            print("Example: python manage_documents.py add --input data/new_docs")
        else:
            ingest_documents(args.input, args.chunk_size)

    elif args.action == 'show':
        show_current_documents()

    elif args.action == 'replace':
        if not args.input:
            print("[ERROR] Error: --input required for replace action")
            print("Example: python manage_documents.py replace --input data/new_docs")
        else:
            confirm = input("[WARNING] This will DELETE all existing documents and replace with new ones. Continue? (yes/no): ")
            if confirm.lower() == 'yes':
                clear_vectorstore()
                ingest_documents(args.input, args.chunk_size)
            else:
                print("[ERROR] Cancelled")
