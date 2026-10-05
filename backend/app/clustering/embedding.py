"""
Embedding generation module.

This module converts incident descriptions into dense vector embeddings
using a pre-trained Sentence Transformer model.

Model Used:
    all-MiniLM-L6-v2

Output:
    List of 384-dimensional embeddings
"""

from typing import List, Optional, Callable

import numpy as np
from sentence_transformers import SentenceTransformer
from app.config.settings import settings
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

            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

            logger.info("Embedding model loaded successfully.")

        except Exception:

            logger.exception("Failed to load embedding model.")

            raise

    def generate_embeddings(
        self,
        texts: List[str],
        check_cancellation: Optional[Callable] = None
    ) -> np.ndarray:
        """
        Generate embeddings for a list of incident texts.

        Args:
            texts:
                List containing incident descriptions.
            check_cancellation:
                Optional callable to cooperatively abort the operation.

        Returns:
            NumPy array of embedding vectors.
        """

        try:

            total = len(texts)
            batch_size = settings.EMBEDDING_BATCH_SIZE

            logger.info(
                "Generating embeddings for %s incidents in batches of %s...",
                total, batch_size
            )

            all_embeddings = []

            for start_idx in range(0, total, batch_size):
                if check_cancellation:
                    check_cancellation()

                batch = texts[start_idx:start_idx + batch_size]
                batch_embeddings = self.model.encode(
                    batch,
                    batch_size=batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
                all_embeddings.append(batch_embeddings)

            if check_cancellation:
                check_cancellation()

            logger.info("Embedding generation completed.")

            return np.vstack(all_embeddings) if all_embeddings else np.array([])

        except Exception as e:
            if type(e).__name__ == "JobCancelledException":
                logger.info("Embedding generation was cancelled.")
                raise

            logger.exception(
                "Embedding generation failed."
            )

            raise
