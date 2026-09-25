"""
Embedding Interface

Defines the contract that every embedding model
must implement.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from abc import ABC
from abc import abstractmethod

from typing import List

import numpy as np


class EmbeddingInterface(ABC):
    """
    Abstract interface for embedding generators.
    """

    @abstractmethod
    def generate_embeddings(
        self,
        texts: List[str]
    ) -> np.ndarray:
        """
        Generate semantic embeddings.

        Parameters
        ----------
        texts : List[str]

        Returns
        -------
        np.ndarray
        """
        pass