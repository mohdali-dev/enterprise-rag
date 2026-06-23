import chromadb
import uuid
import logging
from typing import List, Dict

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Lazy load embeddings to drastically speed up Streamlit's initial boot time
        from langchain_community.embeddings import HuggingFaceEmbeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection_name = "documents"
        self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except Exception:
            # Force cosine similarity so that (1 - distance) accurately yields a 0-1 percentage
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_documents(self, chunks: List[Dict], batch_size: int = 100) -> bool:
        """Adds documents in batches to prevent ChromaDB OOM errors on large files."""
        try:
            if not chunks:
                return False
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                documents = [chunk["content"] for chunk in batch]
                metadatas = [chunk["metadata"] for chunk in batch]
                ids = [str(uuid.uuid4()) for _ in batch]
                
                embeddings = self.embeddings.embed_documents(documents)
                
                self.collection.add(
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                
            return True
        except Exception as e:
            logging.error(f"Error adding documents: {str(e)}")
            return False
            
    def get_all_chunks(self, filter_source: str) -> List[Dict]:
        """Retrieves all text chunks for a specific document (required for Summarization)."""
        try:
            results = self.collection.get(
                where={"source": filter_source},
                include=["documents", "metadatas"]
            )
            
            formatted = []
            if results["documents"]:
                for i in range(len(results["documents"])):
                    formatted.append({
                        "content": results["documents"][i],
                        "metadata": results["metadatas"][i]
                    })
                    
            # Sort chronologically by chunk_index or page to maintain logical reading order
            formatted.sort(key=lambda x: x["metadata"].get("chunk_index", x["metadata"].get("page", 0)))
            
            return formatted
            
        except Exception as e:
            logging.error(f"Error fetching all chunks: {str(e)}")
            return []
    
    def similarity_search(self, query: str, k: int = 5, filter_source: str = None) -> List[Dict]:
        try:
            query_embedding = self.embeddings.embed_query(query)
            
            where = None
            if filter_source:
                where = {"source": filter_source}
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            formatted = []
            if results["documents"] and len(results["documents"]) > 0:
                for i in range(len(results["documents"][0])):
                    formatted.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "score": 1 - results["distances"][0][i]
                    })
            
            return formatted
        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            return []
    
    def get_document_count(self) -> int:
        return self.collection.count()
    
    def get_sources(self) -> List[str]:
        try:
            results = self.collection.get(include=["metadatas"])
            sources = list(set([meta["source"] for meta in results["metadatas"]]))
            return sources
        except Exception as e:
            logging.error(f"Error getting sources: {str(e)}")
            return []
    
    def delete_document(self, source: str):
        try:
            self.collection.delete(where={"source": source})
        except Exception as e:
            logging.error(f"Error deleting document: {str(e)}")
    
    def reset(self):
        try:
            self.client.delete_collection(self.collection_name)
            self._get_or_create_collection()
        except Exception as e:
            logging.error(f"Error resetting database: {str(e)}")