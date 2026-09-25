"""
Processing pipeline stages.

Author: Aman Maurya
"""

from enum import Enum


class ProcessingStage(str, Enum):

    QUEUED = "Queued"

    VALIDATION = "Dataset Validation"

    CLEANING = "Data Cleaning"

    EMBEDDINGS = "Embedding Generation"

    CLUSTERING = "Semantic Clustering"

    CLUSTER_ANALYSIS = "Cluster Analysis"

    RECURRENCE = "Recurrence Detection"

    DATABASE = "Database Persistence"

    COMPLETED = "Completed"

    FAILED = "Failed"