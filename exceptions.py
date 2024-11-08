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
            error_code="DOC_PROCESSING_ERROR",
            status_code=400
        )

class EmbeddingGenerationError(RAGException):
    """Raised when embedding generation fails"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="EMBEDDING_ERROR",
            status_code=500
        )

class VectorStoreError(RAGException):
    """Raised when vector store operations fail"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="VECTOR_STORE_ERROR",
            status_code=500
        )