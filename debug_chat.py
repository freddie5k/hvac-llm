#!/usr/bin/env python3
"""
Debug version to see what's happening with the model
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from crash_monitor import start_monitoring, log_step
from windows_safe_config import WindowsSafeConfig
from rag_system.models.llama import LlamaModel

def debug_model():
    print("[*] Debug mode - checking model response generation")
    
    # Initialize
    monitor = start_monitoring()
    WindowsSafeConfig.check_system_resources()
    
    print("[*] Loading model...")
    model = LlamaModel()
    model.load_model()
    print("[OK] Model loaded!")
    
    # Test different prompt formats
    test_prompts = [
        "Hello",
        "2+2=",
        "What is the capital of France?",
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\nWhat is 2+2?<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Test {i} ---")
        print(f"Prompt: {repr(prompt)}")
        print("Response: ", end="")
        
        try:
            # Get raw tokenizer input
            inputs = model.tokenizer(prompt, return_tensors="pt")
            print(f"\nInput tokens: {inputs['input_ids'].shape}")
            
            # Generate with verbose settings
            import torch
            with torch.no_grad():
                outputs = model.model.generate(
                    inputs['input_ids'].to(model.device),
                    max_new_tokens=50,
                    temperature=0.1,  # Lower temperature
                    do_sample=True,
                    pad_token_id=model.tokenizer.eos_token_id,
                    eos_token_id=model.tokenizer.eos_token_id
                )
            
            # Decode full output
            full_response = model.tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Full output: {repr(full_response)}")
            
            # Extract just the new part
            new_part = full_response[len(prompt):].strip()
            print(f"New part: {repr(new_part)}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    debug_model()