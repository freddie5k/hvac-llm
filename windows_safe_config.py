# Windows-Safe Configuration for RAG System
# This prevents system crashes by adding safety checks

import torch
import psutil
import os

class WindowsSafeConfig:
    @staticmethod
    def check_system_resources():
        """Check if system has enough resources before loading model"""
        # Check available RAM (need at least 12GB for safety)
        ram_gb = psutil.virtual_memory().total / (1024**3)
        if ram_gb < 12:
            raise RuntimeError(f"Insufficient RAM: {ram_gb:.1f}GB. Need at least 12GB")
        
        # Check GPU memory if available
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            if gpu_memory < 6:
                raise RuntimeError(f"Insufficient GPU memory: {gpu_memory:.1f}GB. Need at least 6GB")
            print(f"[OK] GPU detected: {torch.cuda.get_device_name(0)} ({gpu_memory:.1f}GB)")
    
    @staticmethod
    def get_safe_model_config():
        """Return Windows-safe model configuration"""
        return {
            "load_in_4bit": True,
            "bnb_4bit_compute_dtype": torch.float16,
            "bnb_4bit_quant_type": "nf4",
            "bnb_4bit_use_double_quant": True,
            "max_memory": {0: "6GB"},  # Limit GPU memory usage
            "device_map": {"": 0} if torch.cuda.is_available() else "cpu",  # Explicit device mapping
            "torch_dtype": torch.float16,
            "low_cpu_mem_usage": True,
        }
    
    @staticmethod
    def monitor_memory():
        """Monitor system memory during operation"""
        ram_percent = psutil.virtual_memory().percent
        if ram_percent > 85:
            print(f"WARNING: High RAM usage: {ram_percent}%")
        
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated() * 100
            if gpu_memory > 80:
                print(f"WARNING: High GPU memory usage: {gpu_memory:.1f}%")