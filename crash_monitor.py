import datetime
import os
import psutil
import torch
import traceback
import atexit
import signal
import sys

class CrashMonitor:
    def __init__(self):
        self.log_file = "crash_log.txt"
        self.start_time = datetime.datetime.now()
        self.setup_handlers()
        self.log_startup()
    
    def setup_handlers(self):
        # Register cleanup on normal exit
        atexit.register(self.log_normal_exit)
        
        # Register signal handlers for crashes
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
        if hasattr(signal, 'SIGBREAK'):  # Windows
            signal.signal(signal.SIGBREAK, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        self.log_crash(f"Received signal {signum}")
        sys.exit(1)
    
    def log_startup(self):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"STARTUP: {self.start_time}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f}GB\n")
            
            if torch.cuda.is_available():
                f.write(f"GPU: {torch.cuda.get_device_name(0)}\n")
                f.write(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f}GB\n")
            else:
                f.write("GPU: None/CPU mode\n")
            f.write(f"{'='*60}\n")
    
    def log_step(self, step_name):
        with open(self.log_file, "a", encoding="utf-8") as f:
            now = datetime.datetime.now()
            elapsed = (now - self.start_time).total_seconds()
            ram_percent = psutil.virtual_memory().percent
            
            f.write(f"[{elapsed:6.1f}s] {step_name} | RAM: {ram_percent:.1f}%")
            
            if torch.cuda.is_available():
                try:
                    gpu_mem = torch.cuda.memory_allocated() / (1024**3)
                    f.write(f" | GPU: {gpu_mem:.1f}GB")
                except:
                    f.write(" | GPU: Error reading")
            f.write("\n")
    
    def log_crash(self, reason="Unknown crash"):
        with open(self.log_file, "a", encoding="utf-8") as f:
            now = datetime.datetime.now()
            elapsed = (now - self.start_time).total_seconds()
            f.write(f"\n*** CRASH DETECTED at {elapsed:.1f}s ***\n")
            f.write(f"Reason: {reason}\n")
            f.write(f"RAM usage: {psutil.virtual_memory().percent:.1f}%\n")
            
            if torch.cuda.is_available():
                try:
                    f.write(f"GPU memory: {torch.cuda.memory_allocated() / (1024**3):.1f}GB\n")
                except:
                    f.write("GPU memory: Error reading\n")
            
            f.write(f"Stack trace:\n{traceback.format_exc()}\n")
            f.write(f"{'='*60}\n")
    
    def log_normal_exit(self):
        with open(self.log_file, "a", encoding="utf-8") as f:
            now = datetime.datetime.now()
            elapsed = (now - self.start_time).total_seconds()
            f.write(f"NORMAL EXIT after {elapsed:.1f}s\n")
            f.write(f"{'='*60}\n")

# Global monitor instance
monitor = None

def start_monitoring():
    global monitor
    monitor = CrashMonitor()
    return monitor

def log_step(step_name):
    if monitor:
        monitor.log_step(step_name)

def log_crash(reason="Unknown crash"):
    if monitor:
        monitor.log_crash(reason)