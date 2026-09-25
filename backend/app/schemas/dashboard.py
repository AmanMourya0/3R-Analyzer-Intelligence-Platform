"""
Dashboard API Schemas

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from pydantic import BaseModel

from typing import List


# ==========================================================
# Summary
# ==========================================================

class DashboardSummaryResponse(BaseModel):

    total_incidents: int

    total_clusters: int

    problem_candidates: int

    processing_jobs: int


# ==========================================================
# Generic Distribution
# ==========================================================

class DistributionResponse(BaseModel):

    label: str

    value: int


# ==========================================================
# Problem Candidate
# ==========================================================

class ProblemCandidateResponse(BaseModel):

    cluster_id: int

    incident_count: int

    recurrence_score: float

    configuration_item: str

    assignment_group: str

    priority: str


# ==========================================================
# Dashboard
# ==========================================================

class DashboardResponse(BaseModel):

    summary: DashboardSummaryResponse

    cluster_distribution: List[DistributionResponse]

    priority_distribution: List[DistributionResponse]

    region_distribution: List[DistributionResponse]

    application_distribution: List[DistributionResponse]

    assignment_group_distribution: List[DistributionResponse]

    problem_candidates: List[ProblemCandidateResponse]