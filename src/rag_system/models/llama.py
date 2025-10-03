import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class LlamaModel:
    def __init__(self, model_name: Optional[str] = None, quantization: str = "4bit"):
        """
        Initialize Llama model with configurable quantization.

        Args:
            model_name: Model identifier from HuggingFace
            quantization: Quantization type - "4bit", "8bit", or "none"
        """
        self.model_name = model_name or os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
        self.quantization = quantization
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """Load model with specified quantization configuration."""
        # Configure quantization based on setting
        quantization_config = None
        load_in_8bit = False
        load_in_4bit = False

        if self.quantization == "4bit":
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            load_in_4bit = True
        elif self.quantization == "8bit":
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0,
            )
            load_in_8bit = True
        # If "none", no quantization is applied (requires more VRAM)

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            token=os.getenv("HF_TOKEN")
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # Build model loading kwargs
        model_kwargs = {
            "device_map": "auto",
            "torch_dtype": torch.float16,
            "trust_remote_code": True,
            "token": os.getenv("HF_TOKEN")
        }

        if quantization_config:
            model_kwargs["quantization_config"] = quantization_config

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            **model_kwargs
        )
        
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: int = 512, 
        temperature: float = 0.7,
        do_sample: bool = True
    ) -> str:
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        input_length = inputs['input_ids'].shape[1]
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=do_sample,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode only the new tokens (after the input)
        new_tokens = outputs[0][input_length:]
        response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        return response.strip()