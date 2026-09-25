"""
Domain model representing recurrence analysis.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from dataclasses import dataclass

from app.models.cluster_summary import ClusterSummary


@dataclass(slots=True)
class RecurrenceResult:
    """
    Result of recurrence analysis for one cluster.
    """

    cluster_summary: ClusterSummary

    recurrence_score: float

    problem_candidate: bool

    recommendation: str