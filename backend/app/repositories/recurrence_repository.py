"""
Recurrence Repository

Responsible for persisting recurrence analysis.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.recurrence_model import Recurrence

from app.models.recurrence_result import RecurrenceResult

from app.repositories.repository_interface import RepositoryInterface

from app.utils.logger import logger

class RecurrenceRepository(
    RepositoryInterface
):

    def __init__(
        self,
        session: Session
    ):

        self.session = session

    def save(

        self,

        recurrence_results: List[
            RecurrenceResult
        ]

    ) -> None:

        logger.info(

            "Persisting recurrence results..."

        )

        records = []

        for result in recurrence_results:

            records.append(

                Recurrence(

                    cluster_id=result.cluster_summary.cluster_id,

                    recurrence_score=result.recurrence_score,

                    problem_candidate=result.problem_candidate,

                    recommendation=result.recommendation

                )

            )

        self.session.bulk_save_objects(
            records
        )

        logger.info(
            "Recurrence persistence completed."
        )

    def get_problem_candidate_count(self) -> int:
        """
        Return total problem candidates.
        """

        try:

            return (

                self.session.query(

                    func.count(
                        Recurrence.cluster_id
                    )

                )

                .filter(

                    Recurrence.problem_candidate.is_(True)

                )

                .scalar()

                or 0

            )

        except Exception:

            logger.exception(
                "Unable to fetch problem candidates."
            )

            raise


    def get_average_recurrence_score(self) -> float:
        """
        Return average recurrence score.
        """

        try:

            value = (

                self.session.query(

                    func.avg(
                        Recurrence.recurrence_score
                    )

                )

                .scalar()

            )

            return round(

                float(value),

                2

            ) if value else 0.0

        except Exception:

            logger.exception(
                "Unable to fetch recurrence score."
            )

            raise


    def get_all_recurrence_results(self):
        """
        Return recurrence analysis.
        """

        try:

            return (

                self.session.query(

                    Recurrence

                )

                .order_by(

                    Recurrence.cluster_id

                )

                .all()

            )

        except Exception:

            logger.exception(
                "Unable to fetch recurrence data."
            )

            raise

    def delete_all(self) -> None:
        """
        Delete all recurrence analysis.
        """
        try:
            deleted = self.session.query(Recurrence).delete()
            logger.info(
                "Deleted %d recurrence results.",
                deleted
            )
        except Exception:
            logger.exception(
                "Unable to delete recurrence results."
            )
            raise
