# Quick Start Guide - RunPod Deployment

## Step 1: Launch RunPod Pod

1. Go to https://runpod.io and sign in
2. Click **Deploy** → **GPU Cloud**
3. Select template: `RunPod PyTorch 2.1.0` (or similar)
4. Choose GPU: RTX 4090, A6000, or A100 (8GB+ VRAM)
5. Set storage: 30GB minimum
6. Click **Deploy**

## Step 2: Connect to Pod

1. Wait for pod to start (status: Running)
2. Click **Connect** button
3. Select **Web Terminal** (easiest) or **SSH**

## Step 3: Run Automated Setup

In the terminal, run:

```bash
cd /workspace
wget https://raw.githubusercontent.com/freddie5k/hvac-llm/main/runpod_setup.sh
chmod +x runpod_setup.sh
./runpod_setup.sh
```

This will:
- Clone the repository
- Install all dependencies
- Set up Python environment
- Configure PYTHONPATH
- Create necessary directories

## Step 4: Configure Environment

```bash
cd /workspace/hvac-llm
nano .env
```

Add your Hugging Face token:
```
HF_TOKEN=hf_your_token_here
```

Get your token from: https://huggingface.co/settings/tokens

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

## Step 5: Start the System

### Option A: API Server
```bash
cd /workspace/hvac-llm
chmod +x start_server.sh
./start_server.sh
```

The API will be available at `http://localhost:8000`

### Option B: Interactive Chat
```bash
cd /workspace/hvac-llm
chmod +x start_chat.sh
./start_chat.sh
```

## Step 6: Access Your API (if using server)

If you exposed port 8000 in RunPod:
- Your API URL: `https://<pod-id>-8000.proxy.runpod.net`

## Troubleshooting

### Python Version Mismatch
The setup script automatically detects and uses the correct Python version.

### Module Not Found
The setup script automatically sets PYTHONPATH. If you still have issues:
```bash
export PYTHONPATH=/workspace/hvac-llm/src:$PYTHONPATH
```

### Out of Memory
- Reduce `MAX_TOKENS` in `.env` (e.g., `MAX_TOKENS=256`)
- Use smaller GPU or upgrade to larger GPU

### Model Download Issues
- Verify HF_TOKEN is correct in `.env`
- Check internet connection
- Ensure you have access to Llama models on Hugging Face

## Adding Documents

```bash
cd /workspace/hvac-llm
# Upload your documents to data/documents/
# Then run ingestion (if you have the script)
python src/rag_system/utils/ingest_documents.py --input data/documents/
```

## Monitoring

### Check GPU usage:
```bash
watch -n 1 nvidia-smi
```

### Check system resources:
```bash
htop
```

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Next Steps

See [RUNPOD_DEPLOYMENT.md](RUNPOD_DEPLOYMENT.md) for:
- Advanced configuration
- Upgrading to larger models (Llama 3.1/3.3 70B)
- Performance optimization
- Cost management
