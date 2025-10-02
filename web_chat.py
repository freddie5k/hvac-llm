#!/usr/bin/env python3
"""
Web chat interface for the RAG system
Similar to ChatGPT/Claude interface
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sys
import os
import uvicorn
from typing import List, Dict

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from crash_monitor import start_monitoring, log_step
from windows_safe_config import WindowsSafeConfig
from rag_system.models.llama import LlamaModel
from rag_system.generation.rag_pipeline import RAGPipeline

app = FastAPI(title="Local LLM Chat")

# Global instances
model = None
rag_pipeline = None
chat_history = []
use_rag = True  # Default to RAG mode

class ChatMessage(BaseModel):
    message: str
    use_rag: bool = True  # Allow per-message override

class ChatResponse(BaseModel):
    response: str
    status: str
    sources: List[str] = []
    mode: str = "rag"  # "rag" or "direct"

def initialize_rag():
    global rag_pipeline
    if rag_pipeline is None:
        print("[*] Initializing RAG pipeline...")
        monitor = start_monitoring()
        WindowsSafeConfig.check_system_resources()

        log_step("Loading RAG pipeline")
        rag_pipeline = RAGPipeline()
        rag_pipeline.initialize()
        print("[OK] RAG pipeline ready!")
    return rag_pipeline

def initialize_model():
    global model
    if model is None:
        print("[*] Initializing direct model for web interface...")
        monitor = start_monitoring()
        WindowsSafeConfig.check_system_resources()

        log_step("Loading model for web interface")
        model = LlamaModel()
        model.load_model()
        print("[OK] Direct model ready for web chat!")
    return model

@app.on_event("startup")
async def startup_event():
    # Pre-load RAG pipeline on startup (includes model)
    try:
        initialize_rag()
    except Exception as e:
        print(f"Warning: Could not pre-load RAG pipeline: {e}")
        print("[*] Will fall back to direct model mode")

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Local LLM Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f7f7f8;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: white;
            border-bottom: 1px solid #e5e5e5;
            padding: 1rem 2rem;
            text-align: center;
        }
        
        .header h1 {
            color: #333;
            font-size: 1.5rem;
            font-weight: 600;
        }

        .mode-toggle {
            margin-top: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .mode-switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
        }

        .mode-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 24px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .slider {
            background-color: #007bff;
        }

        input:checked + .slider:before {
            transform: translateX(26px);
        }

        .mode-label {
            font-size: 0.9rem;
            color: #666;
        }

        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
            padding: 0 1rem;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 2rem 0;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .message {
            display: flex;
            gap: 0.75rem;
            max-width: 100%;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message.assistant {
            justify-content: flex-start;
        }
        
        .message-content {
            background: white;
            border-radius: 1rem;
            padding: 0.75rem 1rem;
            max-width: 70%;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            white-space: pre-wrap;
        }
        
        .message.user .message-content {
            background: #007bff;
            color: white;
        }
        
        .message.assistant .message-content {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
        }

        .sources {
            margin-top: 0.5rem;
            padding: 0.5rem;
            background: #e7f3ff;
            border-radius: 0.5rem;
            font-size: 0.85rem;
            color: #0066cc;
        }

        .sources strong {
            display: block;
            margin-bottom: 0.25rem;
        }

        .input-container {
            padding: 1rem 0 2rem;
            background: white;
            border-top: 1px solid #e5e5e5;
        }
        
        .input-form {
            display: flex;
            gap: 0.5rem;
            max-width: 800px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        .input-box {
            flex: 1;
            border: 1px solid #d1d5db;
            border-radius: 0.5rem;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            outline: none;
            resize: none;
            min-height: 44px;
            max-height: 120px;
        }
        
        .input-box:focus {
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }
        
        .send-button {
            background: #007bff;
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        
        .send-button:hover:not(:disabled) {
            background: #0056b3;
        }
        
        .send-button:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        
        .typing-indicator {
            display: none;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1rem;
            background: #f8f9fa;
            border-radius: 1rem;
            max-width: 100px;
            margin-left: 0;
        }
        
        .typing-dots {
            display: flex;
            gap: 0.25rem;
        }
        
        .typing-dots span {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: #6c757d;
            animation: typing 1.4s infinite ease-in-out;
        }
        
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes typing {
            0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }
        
        .welcome {
            text-align: center;
            color: #6c757d;
            padding: 2rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Local LLM Chat</h1>
        <p style="color: #666; margin-top: 0.5rem;">Llama 3.1 8B • Running locally on your GPU</p>
        <div class="mode-toggle">
            <span class="mode-label">Direct Chat</span>
            <label class="mode-switch">
                <input type="checkbox" id="ragToggle" checked>
                <span class="slider"></span>
            </label>
            <span class="mode-label"><strong>RAG Mode</strong></span>
        </div>
    </div>
    
    <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
            <div class="welcome">
                <h3>Welcome to your local AI assistant!</h3>
                <p>Ask me anything. I'm running Llama 3.1 8B locally on your machine.</p>
                <p style="margin-top: 1rem; color: #28a745;"><strong>RAG Mode Active:</strong> I can answer questions from your documents!</p>
            </div>
        </div>
        
        <div class="input-container">
            <form class="input-form" id="chatForm">
                <textarea 
                    class="input-box" 
                    id="messageInput" 
                    placeholder="Type your message here..." 
                    rows="1"
                ></textarea>
                <button type="submit" class="send-button" id="sendButton">Send</button>
            </form>
        </div>
    </div>

    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const chatForm = document.getElementById('chatForm');
        
        // Auto-resize textarea
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
        
        // Send on Enter (but not Shift+Enter)
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });
        
        function addMessage(content, sender, sources = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;

            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;

            messageDiv.appendChild(contentDiv);

            // Add sources if available (RAG mode)
            if (sources && sources.length > 0) {
                const sourcesDiv = document.createElement('div');
                sourcesDiv.className = 'sources';
                sourcesDiv.innerHTML = `<strong>Sources:</strong>${sources.map(s => `<div>• ${s}</div>`).join('')}`;
                messageDiv.appendChild(sourcesDiv);
            }

            chatMessages.appendChild(messageDiv);

            // Remove welcome message if present
            const welcome = chatMessages.querySelector('.welcome');
            if (welcome) {
                welcome.remove();
            }

            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function showTypingIndicator() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message assistant';
            typingDiv.innerHTML = `
                <div class="typing-indicator" style="display: flex;">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            `;
            typingDiv.id = 'typingIndicator';
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function hideTypingIndicator() {
            const typing = document.getElementById('typingIndicator');
            if (typing) {
                typing.remove();
            }
        }
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            // Get RAG mode status
            const useRag = document.getElementById('ragToggle').checked;

            // Add user message
            addMessage(message, 'user');

            // Clear input
            messageInput.value = '';
            messageInput.style.height = 'auto';

            // Disable input while processing
            messageInput.disabled = true;
            sendButton.disabled = true;

            // Show typing indicator
            showTypingIndicator();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        use_rag: useRag
                    }),
                });

                const data = await response.json();

                // Hide typing indicator
                hideTypingIndicator();

                if (data.status === 'success') {
                    addMessage(data.response, 'assistant', data.sources || []);
                } else {
                    addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
                }
            } catch (error) {
                hideTypingIndicator();
                addMessage('Sorry, I encountered a connection error. Please try again.', 'assistant');
                console.error('Error:', error);
            }

            // Re-enable input
            messageInput.disabled = false;
            sendButton.disabled = false;
            messageInput.focus();
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    try:
        global model, rag_pipeline, chat_history

        if message.use_rag:
            # RAG mode
            log_step(f"RAG chat: {message.message[:30]}...")

            # Initialize RAG if not loaded
            if rag_pipeline is None:
                rag_pipeline = initialize_rag()

            # Query using RAG (k=8 for more context)
            result = rag_pipeline.query(message.message, k=8)

            # Store in history
            chat_history.append({
                "user": message.message,
                "assistant": result["answer"],
                "sources": result["sources"],
                "mode": "rag"
            })

            return ChatResponse(
                response=result["answer"],
                status="success",
                sources=result["sources"],
                mode="rag"
            )

        else:
            # Direct mode
            log_step(f"Direct chat: {message.message[:30]}...")

            # Initialize model if not loaded
            if model is None:
                model = initialize_model()

            # Create simple prompt
            prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{message.message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

            # Generate response
            response = model.generate_response(
                prompt=prompt,
                max_tokens=512,
                temperature=0.7
            )

            # Store in history
            chat_history.append({
                "user": message.message,
                "assistant": response,
                "mode": "direct"
            })

            return ChatResponse(
                response=response,
                status="success",
                mode="direct"
            )

    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return ChatResponse(
            response="I'm sorry, I encountered an error processing your request.",
            status="error",
            mode="error"
        )

@app.get("/status")
async def get_status():
    global model, rag_pipeline
    return {
        "model_loaded": model is not None,
        "rag_loaded": rag_pipeline is not None,
        "chat_count": len(chat_history),
        "status": "ready" if (model or rag_pipeline) else "loading"
    }

if __name__ == "__main__":
    print("Starting web chat interface...")
    print("Open your browser to: http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)