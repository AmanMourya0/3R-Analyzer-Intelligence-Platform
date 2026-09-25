"""
Dashboard Response Schema
"""

from pydantic import BaseModel
from pydantic import ConfigDict


class DashboardResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    total_incidents: int

    total_clusters: int

    total_problem_candidates: int

    average_cluster_size: float

    average_recurrence_score: float