#!/usr/bin/env python3
"""
Web chat interface for the RAG system - RunPod compatible
Similar to ChatGPT/Claude interface
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sys
import os
import uvicorn
from typing import List

# Add src to path for module imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rag_system.generation.rag_pipeline import RAGPipeline

app = FastAPI(title="RAG Chat Interface")

# Global instances
rag_pipeline = None
chat_history = []

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str
    sources: List[str] = []

@app.on_event("startup")
async def startup_event():
    global rag_pipeline
    try:
        print("[*] Initializing RAG pipeline...")
        rag_pipeline = RAGPipeline()
        rag_pipeline.initialize()
        print("[OK] RAG pipeline ready!")
    except Exception as e:
        print(f"Warning: Could not initialize RAG pipeline: {e}")

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HVAC RAG Chat</title>
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

        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 900px;
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
            max-width: 75%;
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
            max-width: 900px;
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
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1rem;
            background: #f8f9fa;
            border-radius: 1rem;
            max-width: 100px;
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
        <h1>🤖 HVAC RAG Assistant</h1>
        <p style="color: #666; margin-top: 0.5rem;">Llama 3.1 8B • Powered by Retrieval-Augmented Generation</p>
    </div>

    <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
            <div class="welcome">
                <h3>Welcome to your HVAC AI assistant!</h3>
                <p>Ask me questions about HVAC systems and dehumidification.</p>
                <p style="margin-top: 1rem; color: #28a745;"><strong>RAG Mode Active:</strong> I'll search through technical documents to answer your questions!</p>
            </div>
        </div>

        <div class="input-container">
            <form class="input-form" id="chatForm">
                <textarea
                    class="input-box"
                    id="messageInput"
                    placeholder="Ask about HVAC systems, dehumidification, or any technical question..."
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

            // Add sources if available
            if (sources && sources.length > 0) {
                const sourcesDiv = document.createElement('div');
                sourcesDiv.className = 'sources';
                sourcesDiv.innerHTML = `<strong>📚 Sources:</strong>${sources.map(s => `<div>• ${s}</div>`).join('')}`;
                contentDiv.appendChild(sourcesDiv);
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
                <div class="typing-indicator">
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
                        message: message
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
        global rag_pipeline, chat_history

        # Initialize RAG if not loaded
        if rag_pipeline is None:
            return ChatResponse(
                response="System is still initializing. Please wait a moment and try again.",
                status="error",
                sources=[]
            )

        # Query using RAG
        result = rag_pipeline.query(message.message, k=8)

        # Store in history
        chat_history.append({
            "user": message.message,
            "assistant": result["answer"],
            "sources": result["sources"]
        })

        return ChatResponse(
            response=result["answer"],
            status="success",
            sources=result["sources"]
        )

    except Exception as e:
        print(f"Chat error: {e}")
        import traceback
        traceback.print_exc()
        return ChatResponse(
            response="I'm sorry, I encountered an error processing your request.",
            status="error",
            sources=[]
        )

@app.get("/status")
async def get_status():
    global rag_pipeline
    return {
        "rag_loaded": rag_pipeline is not None,
        "chat_count": len(chat_history),
        "status": "ready" if rag_pipeline else "loading"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("=" * 50)
    print("Starting HVAC RAG Web Chat Interface...")
    print("=" * 50)
    print("")
    print("Open your browser to: http://localhost:8080")
    print("Or if on RunPod: https://<pod-id>-8080.proxy.runpod.net")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8080)
