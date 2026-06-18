import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List, Dict
import uuid


class VectorStore:
    def __init__(self):
        self.client = chromadb.Client()
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection_name = "documents"
        self._get_or_create_collection()
    
    def _get_or_create_collection(self):
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except:
            self.collection = self.client.create_collection(name=self.collection_name)
    
    def add_documents(self, chunks: List[Dict]) -> bool:
        try:
            if not chunks:
                return False
            
            documents = [chunk["content"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [str(uuid.uuid4()) for _ in chunks]
            
            embeddings = self.embeddings.embed_documents(documents)
            
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
            return False
    
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
            print(f"Search error: {str(e)}")
            return []
    
    def get_document_count(self) -> int:
        return self.collection.count()
    
    def get_sources(self) -> List[str]:
        try:
            results = self.collection.get(include=["metadatas"])
            sources = list(set([meta["source"] for meta in results["metadatas"]]))
            return sources
        except:
            return []
    
    def delete_document(self, source: str):
        try:
            self.collection.delete(where={"source": source})
        except Exception as e:
            print(f"Error deleting document: {str(e)}")
    
    def reset(self):
        try:
            self.client.delete_collection(self.collection_name)
            self._get_or_create_collection()
        except Exception as e:
            print(f"Error resetting: {str(e)}")