"""
Dashboard Domain Models

Read-model objects used by DashboardService.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from dataclasses import dataclass
from typing import List


# ==========================================================
# Summary
# ==========================================================

@dataclass(slots=True)
class DashboardSummary:

    total_incidents: int

    total_clusters: int

    problem_candidates: int

    processing_jobs: int

    total_runners: int = 0
    total_repeaters: int = 0
    total_rares: int = 0


# ==========================================================
# Generic Distribution Item
# ==========================================================

@dataclass(slots=True)
class DistributionItem:

    label: str

    value: int


# ==========================================================
# Problem Candidate
# ==========================================================

@dataclass(slots=True)
class ProblemCandidate:

    cluster_id: int

    incident_count: int

    recurrence_score: float

    configuration_item: str

    assignment_group: str

    priority: str


# ==========================================================
# Dashboard Aggregate
# ==========================================================

@dataclass(slots=True)
class Dashboard:

    summary: DashboardSummary

    cluster_distribution: List[DistributionItem]

    priority_distribution: List[DistributionItem]

    region_distribution: List[DistributionItem]

    application_distribution: List[DistributionItem]

    assignment_group_distribution: List[DistributionItem]

    problem_candidates: List[ProblemCandidate]