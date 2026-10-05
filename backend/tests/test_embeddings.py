"""
Tests for embedding persistence in pipeline output.
"""

import numpy as np
import pandas as pd

from app.clustering.cluster_analyzer import ClusterAnalyzer
from app.clustering.recurrence import RecurrenceDetector
from app.constants import EMBEDDING
from app.pipelines.incident_pipeline import IncidentPipeline
from app.services.preprocessing import Preprocessor
from app.clustering.three_r_classifier import ThreeRClassifier


class FakeEmbeddingGenerator:

    def generate_embeddings(self, texts, **kwargs):
        return np.array(
            [
                [0.1, 0.2, 0.3],
                [0.4, 0.5, 0.6],
            ]
        )


class FakeClusterer:

    def generate(self, embeddings):
        return np.array([0, 0])


def test_pipeline_stores_embeddings_as_lists():
    dataframe = pd.DataFrame(
        {
            "Incident Number": ["INC001", "INC002"],
            "Short Description": ["Email down", "Email outage"],
            "Description": ["Mail unavailable", "Mail failure"],
            "Category": ["Software", "Software"],
            "Subcategory": ["Email", "Email"],
            "Priority": ["P2", "P2"],
            "State": ["Closed", "Closed"],
            "Assignment Group": ["Messaging", "Messaging"],
            "Configuration Item (Application)": ["Exchange", "Exchange"],
            "Business Service": ["Collaboration", "Collaboration"],
            "Region": ["NA", "NA"],
            "Created Date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "Resolved Date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "Resolution Notes": ["Fixed", "Fixed"],
            "Problem Candidate": [False, False],
        }
    )

    pipeline = object.__new__(IncidentPipeline)
    pipeline.dataset_path = None
    pipeline.preprocessor = Preprocessor()
    pipeline.embedding_generator = FakeEmbeddingGenerator()
    pipeline.cluster_generator = FakeClusterer()
    pipeline.cluster_analyzer = ClusterAnalyzer()
    pipeline.recurrence_detector = RecurrenceDetector()
    pipeline.three_r_classifier = ThreeRClassifier()

    result = pipeline.run(dataframe)

    assert result.dataframe[EMBEDDING].tolist() == [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
    ]
