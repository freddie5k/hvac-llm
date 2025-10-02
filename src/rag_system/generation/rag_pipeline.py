from typing import List, Dict, Any, Optional
from ..models.llama import LlamaModel
from ..retrieval.vector_store import VectorStore
import os
from dotenv import load_dotenv

load_dotenv()

class RAGPipeline:
    def __init__(self, model_name: Optional[str] = None):
        self.llama_model = LlamaModel(model_name)
        self.vector_store = VectorStore()
        self.max_tokens = int(os.getenv("MAX_TOKENS", "512"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.model_loaded = False
        
    def initialize(self):
        self.llama_model.load_model()
        self.vector_store.initialize_collection()
        self.model_loaded = True
        
    def format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.get('metadata', {}).get('source', 'Unknown')
            content = doc.get('content', '')
            context_parts.append(f"[Document {i} - Source: {source}]\n{content}")
        
        return "\n\n".join(context_parts)
    
    def create_prompt(self, query: str, context: str) -> str:
        prompt_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a specialized HVAC dehumidification engineer providing consultation. Be interactive and helpful.

CRITICAL RULES:
1. Use formulas EXACTLY as written in the documentation - never invent values
2. When information is missing, ASK the user for it ONCE - do NOT ask again if already provided
3. PREFER METRIC UNITS (kg/hr, g/kg, m³/hr, °C, %RH) - only use imperial if specifically requested
4. If documentation shows formulas in both metric and imperial, use METRIC version
5. Read the user's previous responses carefully - they may have already provided values you need
6. Never say "let's assume X" - instead say "I need to know: X"
7. After receiving values, PROCEED with the calculation - don't ask for the same values again

RESPONSE FORMAT when information is missing:
1. State what formulas/methods ARE available in the documentation
2. List the SPECIFIC values you need from the user (be precise: "room temperature in °C", "ambient humidity in %RH", etc.)
3. Explain WHY you need each value
4. Optionally show the formula with placeholders so user understands the calculation

<|eot_id|><|start_header_id|>user<|end_header_id|>

Technical Documentation Context:
{context}

User Question: {query}

Instructions: Answer using ONLY the documentation formulas. If you need additional information to calculate accurately, ask the user for specific values. Do not make assumptions - be professional and request the data you need.

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return prompt_template.format(context=context, query=query)
    
    def query(self, question: str, k: int = 8) -> Dict[str, Any]:
        if not self.model_loaded:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        retrieved_docs = self.vector_store.similarity_search(question, k=k)
        
        if not retrieved_docs:
            return {
                "answer": "I don't have any relevant information to answer your question.",
                "sources": [],
                "retrieved_docs": []
            }
        
        context = self.format_context(retrieved_docs)
        prompt = self.create_prompt(question, context)
        
        answer = self.llama_model.generate_response(
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        
        sources = list(set([
            doc.get('metadata', {}).get('source', 'Unknown') 
            for doc in retrieved_docs
        ]))
        
        return {
            "answer": answer,
            "sources": sources,
            "retrieved_docs": retrieved_docs
        }
    
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]] = None, ids: List[str] = None):
        self.vector_store.add_documents(texts, metadatas, ids)