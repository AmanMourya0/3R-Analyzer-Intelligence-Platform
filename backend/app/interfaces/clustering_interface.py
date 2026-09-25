"""
Clustering Interface

Defines the contract for clustering algorithms.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from abc import ABC
from abc import abstractmethod

import numpy as np


class ClusteringInterface(ABC):
    """
    Abstract clustering interface.
    """

    @abstractmethod
    def generate(
        self,
        embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Generate cluster labels.

        Parameters
        ----------
        embeddings : np.ndarray

        Returns
        -------
        np.ndarray
        """
        pass