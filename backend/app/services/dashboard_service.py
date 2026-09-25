"""
Dashboard Service

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from sqlalchemy.orm import Session

from app.models.dashboard import Dashboard
from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:
    """
    Coordinates dashboard analytics.
    """

    def __init__(
        self,
        session: Session
    ):
        self.repository = DashboardRepository(session)

    def get_dashboard(self) -> Dashboard:

        return Dashboard(

            summary=self.repository.get_summary(),

            cluster_distribution=self.repository.get_cluster_distribution(),

            priority_distribution=self.repository.get_priority_distribution(),

            region_distribution=self.repository.get_region_distribution(),

            application_distribution=self.repository.get_application_distribution(),

            assignment_group_distribution=self.repository.get_assignment_group_distribution(),

            problem_candidates=self.repository.get_problem_candidates()

        )