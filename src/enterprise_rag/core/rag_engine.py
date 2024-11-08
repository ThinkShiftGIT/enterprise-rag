from typing import List, Dict, Any
import logging
from .embedding_service import EmbeddingService
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_store: VectorStore
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        logger.info("RAG Engine initialized")

    async def process_query(
        self,
        query: str,
        top_k: int = 3
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Processing query: {query}")
            
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embeddings([query])[0]
            logger.info("Generated query embedding")
            
            # Get relevant documents
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k
            )
            logger.info(f"Found {len(results)} relevant documents")

            # Format response
            response = {
                'query': query,
                'results': results,
                'total_results': len(results),
                'categories': {
                    'Relevant Documents': results
                }
            }

            return response

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise