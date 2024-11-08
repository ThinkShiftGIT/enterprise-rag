import os
from pathlib import Path

def write_file(path, content):
    """Write content to file"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {path}")

def fix_files():
    # Update exceptions.py
    exceptions_content = '''
from enum import Enum

class ErrorCode(str, Enum):
    DOCUMENT_TOO_LARGE = "DOC_001"
    UNSUPPORTED_FORMAT = "DOC_002"
    PROCESSING_ERROR = "DOC_003"
    EMBEDDING_ERROR = "EMB_001"
    VECTOR_STORE_ERROR = "VS_001"

class RAGException(Exception):
    """Base exception for RAG system"""
    def __init__(self, message: str, error_code: str, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class DocumentProcessingError(RAGException):
    """Raised when document processing fails"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code=ErrorCode.PROCESSING_ERROR,
            status_code=400
        )

class EmbeddingGenerationError(RAGException):
    """Raised when embedding generation fails"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code=ErrorCode.EMBEDDING_ERROR,
            status_code=500
        )

class VectorStoreError(RAGException):
    """Raised when vector store operations fail"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code=ErrorCode.VECTOR_STORE_ERROR,
            status_code=500
        )
'''
    write_file('src/enterprise_rag/exceptions.py', exceptions_content)

    # Update vector_store.py
    vector_store_content = '''
import numpy as np
from typing import List, Dict, Any
import chromadb
from ..exceptions import VectorStoreError

class VectorStore:
    def __init__(self, collection_name: str, persist_directory: str):
        """Initialize vector store"""
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(name=collection_name)
        except Exception as e:
            raise VectorStoreError(f"Failed to initialize vector store: {str(e)}")

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray):
        """Add documents and their embeddings to the store"""
        try:
            ids = [str(i) for i in range(len(documents))]
            texts = [doc["text"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to add documents: {str(e)}")

    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            results = self.collection.query(
                query_embeddings=query_embedding.reshape(1, -1).tolist(),
                n_results=top_k
            )
            
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if 'metadatas' in results else {},
                        'score': float(results['distances'][0][i]) if 'distances' in results else 0.0,
                        'id': results['ids'][0][i]
                    })
            
            return formatted_results
        except Exception as e:
            raise VectorStoreError(f"Search failed: {str(e)}")
'''
    write_file('src/enterprise_rag/core/vector_store.py', vector_store_content)

    # Update __init__.py files
    root_init_content = '''
from .exceptions import DocumentProcessingError, EmbeddingGenerationError, VectorStoreError
from .core.document_processor import DocumentProcessor
from .core.embedding_service import EmbeddingService
from .core.vector_store import VectorStore

__version__ = "1.0.0"
'''
    write_file('src/enterprise_rag/__init__.py', root_init_content)

    core_init_content = '''
from .document_processor import DocumentProcessor
from .embedding_service import EmbeddingService
from .vector_store import VectorStore

__all__ = ["DocumentProcessor", "EmbeddingService", "VectorStore"]
'''
    write_file('src/enterprise_rag/core/__init__.py', core_init_content)

if __name__ == "__main__":
    fix_files()
    print("\nFiles updated successfully!")
    print("\nNext steps:")
    print("1. Reinstall the package:")
    print("   pip install -e .")
    print("2. Run the test:")
    print("   python test_pdf_processing.py")