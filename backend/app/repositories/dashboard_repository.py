"""
Dashboard Repository

Read-only analytical queries.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.incident_model import Incident
from app.database.cluster_model import Cluster
from app.database.recurrence_model import Recurrence
from app.database.processing_job_model import ProcessingJob

from app.models.dashboard import (
    DashboardSummary,
    DistributionItem,
    ProblemCandidate
)


class DashboardRepository:

    """
    Read-model repository for dashboard analytics.
    """

    def __init__(
        self,
        session: Session
    ):
        self.session = session

    # =====================================================
    # SUMMARY
    # =====================================================

    def get_summary(self) -> DashboardSummary:

        total_incidents = (
            self.session.query(func.count(Incident.id))
            .scalar()
            or 0
        )

        total_clusters = (
            self.session.query(func.count(Cluster.cluster_id))
            .scalar()
            or 0
        )

        problem_candidates = (
            self.session.query(func.count(Recurrence.cluster_id))
            .filter(
                Recurrence.problem_candidate.is_(True)
            )
            .scalar()
            or 0
        )

        processing_jobs = (
            self.session.query(func.count(ProcessingJob.id))
            .scalar()
            or 0
        )

        return DashboardSummary(
            total_incidents=total_incidents,
            total_clusters=total_clusters,
            problem_candidates=problem_candidates,
            processing_jobs=processing_jobs,
        )

    # =====================================================
    # CLUSTER DISTRIBUTION
    # =====================================================

    def get_cluster_distribution(self):

        rows = (
            self.session.query(
                Cluster.cluster_id,
                Cluster.incident_count
            )
            .order_by(
                Cluster.incident_count.desc()
            )
            .limit(15)
            .all()
        )

        return [

            DistributionItem(

                label=f"Cluster {row.cluster_id}",

                value=row.incident_count

            )

            for row in rows

        ]

    # =====================================================
    # PRIORITY
    # =====================================================

    def get_priority_distribution(self):

        rows = (

            self.session.query(

                Cluster.top_priority,

                func.count(

                    Cluster.cluster_id

                )

            )

            .group_by(

                Cluster.top_priority

            )

            .all()

        )

        return [

            DistributionItem(

                label=row[0],

                value=row[1]

            )

            for row in rows

        ]

    # =====================================================
    # REGION
    # =====================================================

    def get_region_distribution(self):

        rows = (

            self.session.query(

                Cluster.top_region,

                func.count(

                    Cluster.cluster_id

                )

            )

            .group_by(

                Cluster.top_region

            )

            .all()

        )

        return [

            DistributionItem(

                label=row[0],

                value=row[1]

            )

            for row in rows

        ]

    # =====================================================
    # APPLICATIONS
    # =====================================================

    def get_application_distribution(self):

        rows = (

            self.session.query(

                Cluster.top_configuration_item,

                func.count(

                    Cluster.cluster_id

                )

            )

            .group_by(

                Cluster.top_configuration_item

            )

            .order_by(

                func.count(

                    Cluster.cluster_id

                ).desc()

            )

            .limit(10)

            .all()

        )

        return [

            DistributionItem(

                label=row[0],

                value=row[1]

            )

            for row in rows

        ]

    # =====================================================
    # ASSIGNMENT GROUPS
    # =====================================================

    def get_assignment_group_distribution(self):

        rows = (

            self.session.query(

                Cluster.top_assignment_group,

                func.count(

                    Cluster.cluster_id

                )

            )

            .group_by(

                Cluster.top_assignment_group

            )

            .order_by(

                func.count(

                    Cluster.cluster_id

                ).desc()

            )

            .limit(10)

            .all()

        )

        return [

            DistributionItem(

                label=row[0],

                value=row[1]

            )

            for row in rows

        ]

    # =====================================================
    # PROBLEM CANDIDATES
    # =====================================================

    def get_problem_candidates(self):

        rows = (

            self.session.query(

                Recurrence,

                Cluster

            )

            .join(

                Cluster,

                Cluster.cluster_id == Recurrence.cluster_id

            )

            .filter(

                Recurrence.problem_candidate.is_(True)

            )

            .order_by(

                Recurrence.recurrence_score.desc()

            )

            .all()

        )

        results = []

        for recurrence, cluster in rows:

            results.append(

                ProblemCandidate(

                    cluster_id=cluster.cluster_id,

                    incident_count=cluster.incident_count,

                    recurrence_score=round(

                        recurrence.recurrence_score,

                        2

                    ),

                    configuration_item=cluster.top_configuration_item,

                    assignment_group=cluster.top_assignment_group,

                    priority=cluster.top_priority

                )

            )

        return results