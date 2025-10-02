#!/usr/bin/env python3
"""
Windows-Safe launcher for the RAG system
Prevents system crashes by checking resources first
"""

import sys
import traceback
from windows_safe_config import WindowsSafeConfig
from crash_monitor import start_monitoring, log_step, log_crash

def main():
    # Start crash monitoring first
    monitor = start_monitoring()
    print("[*] Crash monitoring started - check crash_log.txt if system crashes")
    
    try:
        log_step("Starting safety checks")
        print("[*] Checking system resources...")
        WindowsSafeConfig.check_system_resources()
        print("[OK] System resources OK")
        
        log_step("Adding Python path")
        # Add src to Python path for imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        
        log_step("Importing chat module")
        # Import after resource check
        from chat import main as chat_main
        
        log_step("Starting RAG system")
        print("[*] Starting RAG system safely...")
        chat_main()
        
    except RuntimeError as e:
        log_crash(f"Safety check failed: {e}")
        print(f"[ERROR] SAFETY CHECK FAILED: {e}")
        print("[INFO] Suggestions:")
        print("- Close other applications to free memory")
        print("- Use CPU-only mode: export CUDA_VISIBLE_DEVICES=''")
        print("- Try a smaller model")
        sys.exit(1)
    except Exception as e:
        log_crash(f"Unexpected error: {e}")
        print(f"[ERROR] UNEXPECTED ERROR: {e}")
        print("[DEBUG] Full traceback:")
        traceback.print_exc()
        print(f"[INFO] Check crash_log.txt for detailed crash information")
        sys.exit(1)

if __name__ == "__main__":
    main()