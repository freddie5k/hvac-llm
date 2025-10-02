#!/usr/bin/env python3
"""
Test RAG system with empty vector store (no documents)
This tests the full RAG pipeline but without retrieval
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from crash_monitor import start_monitoring, log_step
from windows_safe_config import WindowsSafeConfig

def main():
    monitor = start_monitoring()
    print("[*] Starting RAG test mode (empty vector store)")
    
    try:
        log_step("Safety checks for empty RAG")
        WindowsSafeConfig.check_system_resources()
        
        log_step("Initializing RAG pipeline")
        from rag_system.generation.rag_pipeline import RAGPipeline
        
        rag = RAGPipeline()
        rag.initialize()
        print("[OK] RAG pipeline initialized with empty vector store")
        
        print("\n" + "="*50)
        print("RAG Test Mode (No Documents)")
        print("="*50)
        print("The system will respond with 'no relevant information'")
        print("This tests the RAG pipeline safely")
        print("Type 'quit' to exit")
        print("-"*50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                log_step(f"RAG query: {user_input[:30]}...")
                print("Searching (empty) knowledge base...")
                
                result = rag.query(user_input)
                print(f"Assistant: {result['answer']}")
                
                if result['sources']:
                    print(f"Sources: {', '.join(result['sources'])}")
                
            except KeyboardInterrupt:
                print("\n\nSession interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()