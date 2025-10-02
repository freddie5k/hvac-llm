#!/usr/bin/env python3
"""
Direct chat with Llama model (no RAG/documents)
Perfect for testing the model without retrieval
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from crash_monitor import start_monitoring, log_step
from windows_safe_config import WindowsSafeConfig
from rag_system.models.llama import LlamaModel

def main():
    # Start monitoring
    monitor = start_monitoring()
    print("[*] Starting direct chat mode (no RAG documents)")
    
    try:
        # Safety checks
        log_step("Safety checks for direct chat")
        WindowsSafeConfig.check_system_resources()
        
        # Load model with GPU support
        log_step("Loading Llama model on GPU")
        print("[*] Loading Llama 3.1 8B model on GPU...")
        model = LlamaModel()
        model.load_model()
        print("[OK] Model loaded successfully on GPU!")
        
        print("\n" + "="*50)
        print("Direct Chat Mode (No RAG)")
        print("="*50)
        print("Ask questions directly to Llama 3.1 8B")
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
                
                log_step(f"Generating response to: {user_input[:30]}...")
                print("Assistant: ", end="", flush=True)
                
                # Create a simple prompt for Llama 3.1
                prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{user_input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
                
                response = model.generate_response(
                    prompt=prompt,
                    max_tokens=512,
                    temperature=0.7
                )
                
                print(response)
                
            except KeyboardInterrupt:
                print("\n\nSession interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                
    except Exception as e:
        print(f"[ERROR] {e}")
        return

if __name__ == "__main__":
    main()