"""
Semantic Clustering Module

Generates semantic clusters from incident embeddings
using HDBSCAN.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

import numpy as np
import hdbscan

from app.interfaces.clustering_interface import ClusteringInterface

from app.config.settings import (
    MIN_CLUSTER_SIZE,
    MIN_SAMPLES,
    CLUSTER_SELECTION_METHOD,
    CLUSTER_METRIC
)

from app.utils.logger import logger


class SemanticClusterer(ClusteringInterface):
    """
    Generates semantic clusters using HDBSCAN.
    """

    def __init__(self) -> None:

        logger.info("Initializing HDBSCAN Cluster Generator...")

        self.clusterer = hdbscan.HDBSCAN(

            min_cluster_size=MIN_CLUSTER_SIZE,

            min_samples=MIN_SAMPLES,

            metric=CLUSTER_METRIC,

            cluster_selection_method=CLUSTER_SELECTION_METHOD
        )

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
            Cluster labels.
        """

        try:

            logger.info("Generating semantic clusters...")

            labels = self.clusterer.fit_predict(
                embeddings
            )

            logger.info(
                "Cluster generation completed."
            )

            return labels

        except Exception:

            logger.exception(
                "Cluster generation failed."
            )

            raise