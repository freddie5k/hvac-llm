#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv
from rag_system.generation.rag_pipeline import RAGPipeline
from rag_system.utils.document_processor import DocumentProcessor

load_dotenv()

def main():
    print("Initializing RAG System...")
    rag_pipeline = RAGPipeline()
    
    try:
        rag_pipeline.initialize()
        print("✅ RAG system initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        return
    
    print("\n" + "="*50)
    print("🤖 RAG Chat Interface")
    print("="*50)
    print("Type 'quit' or 'exit' to end the session")
    print("Type 'help' for available commands")
    print("-"*50)
    
    while True:
        try:
            user_input = input("\n💬 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("- Ask any question about your documents")
                print("- 'quit' or 'exit': End the session")
                print("- 'help': Show this help message")
                continue
            
            if not user_input:
                continue
            
            print("🔍 Searching knowledge base...")
            result = rag_pipeline.query(user_input)
            
            print(f"\n🤖 Assistant: {result['answer']}")
            
            if result['sources']:
                print(f"\n📚 Sources: {', '.join(result['sources'])}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()