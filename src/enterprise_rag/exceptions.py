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
