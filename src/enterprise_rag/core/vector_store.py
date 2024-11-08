import numpy as np
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import logging
import uuid

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, collection_name: str, persist_directory: str):
        try:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get collection
            try:
                self.collection = self.client.get_collection(collection_name)
                logger.info(f"Retrieved existing collection: {collection_name}")
            except:
                self.collection = self.client.create_collection(collection_name)
                logger.info(f"Created new collection: {collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray):
        try:
            # Generate unique IDs
            ids = [str(uuid.uuid4()) for _ in range(len(documents))]
            
            # Prepare data
            texts = [doc["text"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            # Add to collection
            self.collection.add(
                documents=texts,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        try:
            # Ensure we don't request more results than we have documents
            count = self.collection.count()
            if count == 0:
                logger.warning("Vector store is empty")
                return []
                
            actual_k = min(top_k, count)
            logger.info(f"Searching for top {actual_k} results")
            
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=actual_k
            )
            
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'score': float(results['distances'][0][i]) if 'distances' in results else 0.0,
                        'id': results['ids'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def clear(self):
        """Clear all documents from the collection"""
        try:
            self.collection.delete(ids=self.collection.get()['ids'])
            logger.info("Cleared vector store")
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            raise

    def is_empty(self) -> bool:
        return self.collection.count() == 0