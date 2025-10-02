import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class VectorStore:
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or os.getenv("VECTOR_DB_PATH", "data/vectorstore")
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        # Force embedding model to CPU to save GPU memory for LLM
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        self.collection_name = "documents"
        self.collection = None
        
    def initialize_collection(self):
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except (ValueError, Exception):
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]] = None, ids: List[str] = None):
        if self.collection is None:
            self.initialize_collection()
            
        embeddings = self.embedding_model.encode(texts).tolist()
        
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(texts))]
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in texts]
            
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if self.collection is None:
            self.initialize_collection()
            
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k
        )
        
        documents = []
        for i in range(len(results['documents'][0])):
            documents.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return documents
    
    def delete_collection(self):
        if self.collection:
            self.client.delete_collection(self.collection_name)
            self.collection = None