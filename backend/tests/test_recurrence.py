"""
Tests for recurrence detection.
"""

from app.clustering.recurrence import RecurrenceDetector
from app.models.cluster_summary import ClusterSummary


def test_recurrence_detector_flags_high_scoring_cluster():
    summary = ClusterSummary(
        cluster_id=7,
        incident_count=20,
        top_configuration_item="Exchange",
        top_assignment_group="Messaging",
        top_region="NA",
        top_priority="P1",
        configuration_item_distribution={"Exchange": 20},
        assignment_group_distribution={"Messaging": 20},
        region_distribution={"NA": 20},
        priority_distribution={"P1": 11},
        first_incident_date="2026-01-01",
        last_incident_date="2026-01-31",
    )

    results = RecurrenceDetector().detect([summary])

    assert len(results) == 1
    assert results[0].recurrence_score == 55
    assert results[0].problem_candidate is True
