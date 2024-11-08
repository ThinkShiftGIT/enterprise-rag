from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import torch
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
        logger.info(f"Embedding service initialized with model {model_name} on {self.device}")

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = self.model.encode(texts, convert_to_tensor=True)
            embeddings_np = embeddings.cpu().numpy()
            logger.info(f"Generated embeddings with shape {embeddings_np.shape}")
            return embeddings_np
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise