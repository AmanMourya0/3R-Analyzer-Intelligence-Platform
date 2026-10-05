"""
Tests for the incident pipeline clustering contract.
"""

import numpy as np
import pandas as pd

from app.clustering.cluster_analyzer import ClusterAnalyzer
from app.clustering.recurrence import RecurrenceDetector
from app.constants import CLUSTER_ID
from app.pipelines.incident_pipeline import IncidentPipeline
from app.services.preprocessing import Preprocessor
from app.clustering.three_r_classifier import ThreeRClassifier


class FakeEmbeddingGenerator:

    def generate_embeddings(self, texts, **kwargs):
        return np.array(
            [
                [1.0, 0.0],
                [0.9, 0.1],
                [0.0, 1.0],
            ]
        )


class FakeClusterer:

    def generate(self, embeddings):
        return np.array([0, 0, -1])


def sample_dataframe():
    return pd.DataFrame(
        {
            "Incident Number": ["INC001", "INC002", "INC003"],
            "Short Description": ["Email down", "Email outage", "VPN slow"],
            "Description": ["Mail unavailable", "Mail failure", "VPN latency"],
            "Category": ["Software", "Software", "Network"],
            "Subcategory": ["Email", "Email", "VPN"],
            "Priority": ["P2", "P2", "P4"],
            "State": ["Closed", "Closed", "Closed"],
            "Assignment Group": ["Messaging", "Messaging", "Network"],
            "Configuration Item (Application)": ["Exchange", "Exchange", "VPN"],
            "Business Service": ["Collaboration", "Collaboration", "Remote"],
            "Region": ["NA", "NA", "EU"],
            "Created Date": pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03"]
            ),
            "Resolved Date": pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03"]
            ),
            "Resolution Notes": ["Fixed", "Fixed", "Fixed"],
            "Problem Candidate": [False, False, False],
        }
    )


def test_pipeline_assigns_cluster_ids_without_loading_model():
    pipeline = object.__new__(IncidentPipeline)
    pipeline.dataset_path = None
    pipeline.preprocessor = Preprocessor()
    pipeline.embedding_generator = FakeEmbeddingGenerator()
    pipeline.cluster_generator = FakeClusterer()
    pipeline.cluster_analyzer = ClusterAnalyzer()
    pipeline.recurrence_detector = RecurrenceDetector()
    pipeline.three_r_classifier = ThreeRClassifier()

    result = pipeline.run(sample_dataframe())

    assert result.dataframe[CLUSTER_ID].tolist() == [0, 0, -1]
    assert len(result.cluster_summaries) == 1
    assert result.cluster_summaries[0].cluster_id == 0
