"""
Application Settings

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""



# -------------------------------------------------------
# Embedding Model Configuration
# -------------------------------------------------------

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

EMBEDDING_BATCH_SIZE = 512

# ==========================================================
# HDBSCAN Configuration
# ==========================================================

MIN_CLUSTER_SIZE = 5

MIN_SAMPLES = 3

CLUSTER_SELECTION_METHOD = "eom"

CLUSTER_METRIC = "euclidean"

# -------------------------------------------------------
# Logging
# -------------------------------------------------------

LOG_LEVEL = "INFO"

# -------------------------------------------------------
# Future Similarity Threshold
# -------------------------------------------------------

SIMILARITY_THRESHOLD = 0.85

# ==========================================================
# Priority Weights
# ==========================================================

PRIORITY_WEIGHTS = {
    "P1": 5,
    "P2": 4,
    "P3": 3,
    "P4": 2,
    "P5": 1
}

# ==========================================================
# Recurrence Threshold
# ==========================================================

PROBLEM_CANDIDATE_THRESHOLD = 50

