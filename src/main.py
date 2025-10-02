from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from rag_system.generation.rag_pipeline import RAGPipeline
from rag_system.utils.document_processor import DocumentProcessor

app = FastAPI(title="RAG System API", version="1.0.0")

rag_pipeline = RAGPipeline()
document_processor = DocumentProcessor()

class QueryRequest(BaseModel):
    question: str
    k: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]

class DocumentUpload(BaseModel):
    content: str
    metadata: Optional[dict] = None

@app.on_event("startup")
async def startup_event():
    try:
        rag_pipeline.initialize()
        print("RAG pipeline initialized successfully")
    except Exception as e:
        print(f"Failed to initialize RAG pipeline: {e}")
        raise

@app.get("/")
async def root():
    return {"message": "RAG System API is running"}

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        result = rag_pipeline.query(request.question, k=request.k)
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_document")
async def add_document(document: DocumentUpload):
    try:
        chunks = document_processor.chunk_text(document.content)
        metadatas = [document.metadata or {} for _ in chunks]
        ids = [f"{document.metadata.get('source', 'unknown')}_{i}" for i in range(len(chunks))]
        
        rag_pipeline.add_documents(chunks, metadatas, ids)
        return {"message": f"Added {len(chunks)} chunks to the vector store"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)