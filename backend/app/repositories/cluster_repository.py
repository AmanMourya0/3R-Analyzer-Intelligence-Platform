"""
Cluster Repository

Responsible for persisting semantic cluster summaries.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.cluster_model import Cluster
from app.models.cluster_summary import ClusterSummary
from app.repositories.repository_interface import RepositoryInterface
from app.utils.logger import logger

class ClusterRepository(RepositoryInterface):
    """
    Repository responsible for Cluster persistence.
    """

    def __init__(self, session: Session):

        self.session = session

    def save(
        self,
        summaries: List[ClusterSummary]
    ) -> None:

        logger.info(
            "Persisting %d cluster summaries...",
            len(summaries)
        )

        cluster_records = []

        for summary in summaries:

            cluster_records.append(

                Cluster(

                    cluster_id=summary.cluster_id,

                    cluster_name=getattr(summary, "cluster_name", "") or "",

                    incident_count=summary.incident_count,

                    top_configuration_item=summary.top_configuration_item,

                    top_assignment_group=summary.top_assignment_group,

                    top_region=summary.top_region,

                    top_priority=summary.top_priority,

                    three_r_category=getattr(summary, "three_r_category", "") or None,

                    three_r_reason=getattr(summary, "three_r_reason", "") or None

                )

            )

        self.session.bulk_save_objects(
            cluster_records
        )

        logger.info(
            "Cluster persistence completed."
        )

    def get_total_clusters(self) -> int:
        """
        Return total clusters.
        """

        try:

            return (

                self.session.query(

                    func.count(
                        Cluster.cluster_id
                    )

                )

                .scalar()

                or 0

            )

        except Exception:

            logger.exception(
                "Unable to fetch cluster count."
            )

            raise


    def get_all_clusters(self):
        """
        Return all clusters.
        """

        try:

            return (

                self.session.query(
                    Cluster
                )

                .order_by(
                    Cluster.cluster_id
                )

                .all()

            )

        except Exception:

            logger.exception(
                "Unable to fetch clusters."
            )

            raise

    def delete_all(self) -> None:
        """
        Delete all cluster summaries.
        """
        try:
            deleted = self.session.query(Cluster).delete()
            logger.info(
                "Deleted %d cluster summaries.",
                deleted
            )
        except Exception:
            logger.exception(
                "Unable to delete cluster summaries."
            )
            raise
