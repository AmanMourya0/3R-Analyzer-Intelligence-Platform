"""
Embedding generation module.

This module converts incident descriptions into dense vector embeddings
using a pre-trained Sentence Transformer model.

Model Used:
    all-MiniLM-L6-v2

Output:
    List of 384-dimensional embeddings
"""

from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer
from app.config.settings import EMBEDDING_MODEL
from app.config.settings import EMBEDDING_BATCH_SIZE
from app.utils.logger import logger


from app.interfaces.embedding_interface import EmbeddingInterface

class SemanticEmbeddingGenerator(EmbeddingInterface):
    """
    Generates semantic embeddings for incidents.
    """

    def __init__(self) -> None:
        """
        Load the Sentence Transformer model only once.

        Loading the model is expensive, so we initialize it
        during object creation and reuse it.
        """
        try:

            logger.info("Loading Sentence Transformer model...")

            self.model = SentenceTransformer(EMBEDDING_MODEL)

            logger.info("Embedding model loaded successfully.")

        except Exception:

            logger.exception("Failed to load embedding model.")

            raise

    def generate_embeddings(
    self,
    texts: List[str]
) -> np.ndarray:
        """
        Generate embeddings for a list of incident texts.

        Args:
            texts:
                List containing incident descriptions.

        Returns:
            NumPy array of embedding vectors.
        """

        try:

            logger.info(
                "Generating embeddings for %s incidents...",
                len(texts)
            )

            embeddings = self.model.encode(
                texts,
                batch_size=EMBEDDING_BATCH_SIZE,
                show_progress_bar=True,
                convert_to_numpy=True
            )

            logger.info("Embedding generation completed.")

            return embeddings

        except Exception:

            logger.exception(
                "Embedding generation failed."
            )

            raise
