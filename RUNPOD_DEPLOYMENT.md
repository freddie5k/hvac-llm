# RunPod Deployment Guide

## Overview
This guide helps you deploy the RAG system on RunPod.io GPU instances, enabling you to run larger models with better performance.

## GPU Recommendations

### Current Model (Llama 3.1 8B with 4-bit quantization)
- **Minimum**: 8GB VRAM (RTX 3060, RTX 4060)
- **Recommended**: 12GB+ VRAM (RTX 3080, RTX 4070)

### Larger Models
- **Llama 3.1 70B (4-bit)**: 40GB+ VRAM (A100 40GB, A6000)
- **Llama 3.1 70B (8-bit)**: 80GB+ VRAM (A100 80GB)
- **Llama 3.3 70B**: Similar requirements to 3.1 70B

## Deployment Methods

### Method 1: Quick Start (Recommended for Testing)

1. **Create RunPod Account**
   - Go to https://runpod.io
   - Sign up and add credits

2. **Launch Pod**
   - Click "Deploy" → "GPU Cloud"
   - Select a GPU template: `RunPod PyTorch 2.1.0`
   - Choose GPU (e.g., RTX 4090, A6000, or A100)
   - Select storage (30GB minimum)
   - Click "Deploy"

3. **Access Pod**
   - Wait for pod to start
   - Click "Connect" → "Start Jupyter Lab" or "SSH over exposed TCP"

4. **Run Setup Script**
   ```bash
   # In the pod terminal
   cd /workspace
   wget https://raw.githubusercontent.com/freddie5k/hvac-llm/main/runpod_setup.sh
   chmod +x runpod_setup.sh
   ./runpod_setup.sh
   ```

5. **Configure Environment**
   ```bash
   cd hvac-llm
   nano .env
   # Add your HF_TOKEN
   ```

6. **Start the Service**
   ```bash
   # Option 1: API Server
   python src/main.py

   # Option 2: Interactive Chat
   python interactive_chat.py
   ```

### Method 2: Docker Deployment (Production)

1. **Build Docker Image Locally**
   ```bash
   docker build -t hvac-rag:latest .
   ```

2. **Push to Docker Hub** (optional)
   ```bash
   docker tag hvac-rag:latest yourusername/hvac-rag:latest
   docker push yourusername/hvac-rag:latest
   ```

3. **Deploy on RunPod**
   - Create custom template with your Docker image
   - Set environment variables in RunPod dashboard
   - Deploy pod with your template

### Method 3: Direct Clone and Run

1. **SSH into RunPod Pod**
   ```bash
   ssh root@<pod-ip> -p <pod-port> -i ~/.ssh/id_ed25519
   ```

2. **Clone and Setup**
   ```bash
   cd /workspace
   git clone https://github.com/freddie5k/hvac-llm.git
   cd hvac-llm
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

3. **Configure and Run**
   ```bash
   cp .env.example .env
   nano .env  # Add HF_TOKEN
   python src/main.py
   ```

## Upgrading to Larger Models

### Llama 3.1 70B (4-bit quantization)

Update your `.env`:
```bash
MODEL_NAME=meta-llama/Llama-3.1-70B-Instruct
MAX_TOKENS=1024
```

GPU Requirements: 40GB+ VRAM

### Llama 3.3 70B

Update your `.env`:
```bash
MODEL_NAME=meta-llama/Llama-3.3-70B-Instruct
MAX_TOKENS=1024
```

GPU Requirements: 40GB+ VRAM

### Model Configuration Options

Edit `src/rag_system/models/llama.py` for advanced configurations:

**For more memory efficiency (slower)**:
```python
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)
```

**For better quality (needs more VRAM)**:
```python
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0,
)
```

## Exposing the API

### Using RunPod HTTP Ports

1. **Configure Exposed Ports** in RunPod dashboard:
   - Add HTTP port 8000

2. **Access API**:
   - Your API will be available at: `https://<pod-id>-8000.proxy.runpod.net`

### Using Gradio/Streamlit (Alternative)

Create a web interface that automatically gets a public URL:
```python
import gradio as gr

def query_rag(question):
    result = rag_pipeline.query(question)
    return result["answer"]

demo = gr.Interface(fn=query_rag, inputs="text", outputs="text")
demo.launch(share=True)  # Creates public URL
```

## Performance Optimization

### 1. Use Flash Attention (if available)
```bash
pip install flash-attn --no-build-isolation
```

Then update model loading with `attn_implementation="flash_attention_2"`

### 2. Increase Batch Size
For multiple queries, batch them together for better GPU utilization.

### 3. Enable Model Caching
Set in `.env`:
```bash
HF_HOME=/workspace/.cache/huggingface
```

## Cost Management

- **On-Demand Pods**: Pay per second, can pause/resume
- **Spot Pods**: Cheaper but can be interrupted
- **Community Cloud**: Most affordable, shared resources

### Estimated Costs (as of 2024)
- RTX 4090: ~$0.40/hour
- A6000 (48GB): ~$0.80/hour
- A100 (80GB): ~$1.50-2.50/hour

## Troubleshooting

### Out of Memory Error
- Reduce `MAX_TOKENS` in `.env`
- Use smaller batch size
- Switch to more aggressive quantization
- Upgrade to larger GPU

### Model Download Issues
- Ensure HF_TOKEN is valid
- Check internet connectivity
- Increase timeout settings

### Slow Response Times
- Enable Flash Attention
- Use faster GPU
- Reduce document retrieval count (k parameter)

## Monitoring

### GPU Usage
```bash
watch -n 1 nvidia-smi
```

### Resource Usage
```bash
htop
```

### Logs
```bash
tail -f logs/app.log
```

## Next Steps

1. Upload your documents to `data/documents/`
2. Run document ingestion: `python src/rag_system/utils/ingest_documents.py --input data/documents/`
3. Test queries via API or interactive chat
4. Monitor GPU usage and adjust model size accordingly

## Support

- RunPod Documentation: https://docs.runpod.io
- Hugging Face Model Hub: https://huggingface.co/meta-llama
- Project Issues: https://github.com/freddie5k/hvac-llm/issues
