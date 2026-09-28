import pytest
import pandas as pd
import numpy as np

from app.clustering.three_r_classifier import ThreeRClassifier, cosine_similarity_vectors
from app.models.cluster_summary import ClusterSummary
from app.models.recurrence_result import RecurrenceResult
from app.constants import (
    CLUSTER_ID,
    THREE_R_CATEGORY,
    SEMANTIC_MATCH_CLUSTER_ID,
    THREE_R_RUNNER,
    THREE_R_REPEATER,
    THREE_R_RARE,
    NOISE_CLUSTER
)

@pytest.fixture
def classifier():
    return ThreeRClassifier()

def test_cosine_similarity():
    vec1 = np.array([1, 0, 0])
    vectors = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [-1, 0, 0]
    ])
    sims = cosine_similarity_vectors(vec1, vectors)
    assert sims[0] == pytest.approx(1.0)
    assert sims[1] == pytest.approx(0.0)
    assert sims[2] == pytest.approx(-1.0)

def test_empty_dataset(classifier):
    df = pd.DataFrame(columns=[CLUSTER_ID])
    embeddings = np.array([])
    df_out, _, summary = classifier.classify(df, embeddings, [], [])
    
    assert len(df_out) == 0
    assert summary.total == 0
    assert summary.runner_count == 0

def test_all_noise_dataset(classifier):
    df = pd.DataFrame({CLUSTER_ID: [NOISE_CLUSTER, NOISE_CLUSTER]})
    embeddings = np.array([[1.0, 0.0], [0.0, 1.0]])
    df_out, _, summary = classifier.classify(df, embeddings, [], [])
    
    assert summary.total == 2
    assert summary.rare_count == 2
    assert all(df_out[THREE_R_CATEGORY] == THREE_R_RARE)

def test_high_priority_alone_is_repeater(classifier):
    # Cluster 2 scenario: High priority (83%), low velocity (0.13), no PC, not top quartile
    df = pd.DataFrame({CLUSTER_ID: [1]*6})
    embeddings = np.ones((6, 2))
    
    cs = ClusterSummary(
        cluster_id=1, incident_count=6,
        priority_distribution={'High': 5, 'Medium': 1},
        first_incident_date="2026-01-01", last_incident_date="2026-02-15", # 45 days span
        top_configuration_item="", top_assignment_group="", top_region="", top_priority="",
        configuration_item_distribution={}, assignment_group_distribution={}, region_distribution={}
    )
    rr = RecurrenceResult(cluster_summary=cs, recurrence_score=6.0, problem_candidate=False, recommendation="")
    
    df_out, summaries, summary = classifier.classify(df, embeddings, [cs], [rr])
    assert summaries[0].three_r_category == THREE_R_REPEATER
    assert summaries[0].three_r_reason.startswith("Normal recurring")

def test_sustained_high_activity(classifier):
    # Cluster 3 scenario: top quartile volume, span >= 14
    df = pd.DataFrame({CLUSTER_ID: [1]*15})
    embeddings = np.ones((15, 2))
    
    cs = ClusterSummary(
        cluster_id=1, incident_count=15, priority_distribution={'Low': 15},
        first_incident_date="2026-01-01", last_incident_date="2026-01-20", # 19 days span
        top_configuration_item="", top_assignment_group="", top_region="", top_priority="",
        configuration_item_distribution={}, assignment_group_distribution={}, region_distribution={}
    )
    rr = RecurrenceResult(cluster_summary=cs, recurrence_score=15.0, problem_candidate=False, recommendation="")
    
    # We need 3 clusters to trigger top quartile logic
    cs2 = ClusterSummary(
        cluster_id=2, incident_count=2, priority_distribution={'Low': 2},
        first_incident_date="2026-01-01", last_incident_date="2026-01-20",
        top_configuration_item="", top_assignment_group="", top_region="", top_priority="",
        configuration_item_distribution={}, assignment_group_distribution={}, region_distribution={}
    )
    rr2 = RecurrenceResult(cluster_summary=cs2, recurrence_score=2.0, problem_candidate=False, recommendation="")
    
    cs3 = ClusterSummary(
        cluster_id=3, incident_count=2, priority_distribution={'Low': 2},
        first_incident_date="2026-01-01", last_incident_date="2026-01-20",
        top_configuration_item="", top_assignment_group="", top_region="", top_priority="",
        configuration_item_distribution={}, assignment_group_distribution={}, region_distribution={}
    )
    rr3 = RecurrenceResult(cluster_summary=cs3, recurrence_score=2.0, problem_candidate=False, recommendation="")
    
    df_all = pd.DataFrame({CLUSTER_ID: [1]*15 + [2]*2 + [3]*2})
    emb_all = np.ones((19, 2))
    
    df_out, summaries, summary = classifier.classify(df_all, emb_all, [cs, cs2, cs3], [rr, rr2, rr3])
    assert summaries[0].three_r_category == THREE_R_RUNNER # Cluster 1 is Runner
    assert summaries[0].three_r_reason == "Sustained high-volume recurring activity"
    assert summaries[1].three_r_category == THREE_R_REPEATER
    assert summaries[2].three_r_category == THREE_R_REPEATER

def test_high_velocity_burst_without_support_is_repeater(classifier):
    # Cluster 0 scenario: velocity 1.25, volume 5, span 4. No prio support, no PC.
    df = pd.DataFrame({CLUSTER_ID: [1]*5})
    embeddings = np.ones((5, 2))
    
    cs = ClusterSummary(
        cluster_id=1, incident_count=5, priority_distribution={'Low': 5},
        first_incident_date="2026-01-01", last_incident_date="2026-01-05", # 4 days
        top_configuration_item="", top_assignment_group="", top_region="", top_priority="",
        configuration_item_distribution={}, assignment_group_distribution={}, region_distribution={}
    )
    rr = RecurrenceResult(cluster_summary=cs, recurrence_score=5.0, problem_candidate=False, recommendation="")
    
    df_out, summaries, summary = classifier.classify(df, embeddings, [cs], [rr])
    assert summaries[0].three_r_category == THREE_R_REPEATER

def test_high_velocity_burst_with_support_is_runner(classifier):
    df = pd.DataFrame({CLUSTER_ID: [1]*5})
    embeddings = np.ones((5, 2))
    
    cs = ClusterSummary(
        cluster_id=1, incident_count=5, priority_distribution={'Low': 5},
        first_incident_date="2026-01-01", last_incident_date="2026-01-05", # 4 days
        top_configuration_item="", top_assignment_group="", top_region="", top_priority="",
        configuration_item_distribution={}, assignment_group_distribution={}, region_distribution={}
    )
    rr = RecurrenceResult(cluster_summary=cs, recurrence_score=5.0, problem_candidate=True, recommendation="") # PC = True acts as support
    
    df_out, summaries, summary = classifier.classify(df, embeddings, [cs], [rr])
    assert summaries[0].three_r_category == THREE_R_RUNNER
    assert summaries[0].three_r_reason == "High-velocity burst with supporting impact/problem signal"

def test_noise_matching(classifier, monkeypatch):
    from app.config.settings import settings
    monkeypatch.setattr(settings, "SIMILARITY_THRESHOLD", 0.85)
    
    df = pd.DataFrame({CLUSTER_ID: [1, 1, NOISE_CLUSTER, NOISE_CLUSTER]})
    embeddings = np.array([
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0], # match
        [0.0, 1.0, 0.0], # no match
    ])
    
    cs = ClusterSummary(
        cluster_id=1, incident_count=2, priority_distribution={'Low': 2},
        first_incident_date="2023-01-01", last_incident_date="2023-01-01",
        top_configuration_item="", top_assignment_group="", top_region="", top_priority="",
        configuration_item_distribution={}, assignment_group_distribution={}, region_distribution={}
    )
    rr = RecurrenceResult(cluster_summary=cs, recurrence_score=10.0, problem_candidate=False, recommendation="")
    
    df_out, _, summary = classifier.classify(df, embeddings, [cs], [rr])
    
    assert df_out.iloc[2][SEMANTIC_MATCH_CLUSTER_ID] == 1
    assert df_out.iloc[2][THREE_R_CATEGORY] == THREE_R_REPEATER
    assert df_out.iloc[3][SEMANTIC_MATCH_CLUSTER_ID] is None
    assert df_out.iloc[3][THREE_R_CATEGORY] == THREE_R_RARE
