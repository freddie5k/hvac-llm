#!/usr/bin/env python3
"""
Interactive chat with pre-loaded model (works with Claude Code)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from crash_monitor import start_monitoring, log_step
from windows_safe_config import WindowsSafeConfig
from rag_system.models.llama import LlamaModel

# Global model instance
model = None

def initialize_model():
    global model
    if model is None:
        print("[*] Initializing model...")
        monitor = start_monitoring()
        WindowsSafeConfig.check_system_resources()
        
        log_step("Loading Llama model on GPU")
        model = LlamaModel()
        model.load_model()
        print("[OK] Model ready for chat!")
    return model

def chat_with_model(user_input):
    global model
    if model is None:
        model = initialize_model()
    
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful AI assistant. Answer questions directly and concisely.

<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_input}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    
    response = model.generate_response(
        prompt=prompt,
        max_tokens=512,
        temperature=0.7
    )
    
    return response

if __name__ == "__main__":
    # Pre-load the model
    initialize_model()
    
    print("\nChat is ready! You can now ask questions.")
    print("Example: python -c \"from interactive_chat import chat_with_model; print(chat_with_model('What is AI?'))\"")