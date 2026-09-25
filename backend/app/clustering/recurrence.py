"""
Recurrence Detection Module

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from typing import List

from app.config.settings import (
    PRIORITY_WEIGHTS,
    PROBLEM_CANDIDATE_THRESHOLD
)

from app.models.cluster_summary import ClusterSummary
from app.models.recurrence_result import RecurrenceResult

from app.utils.logger import logger


class RecurrenceDetector:
    """
    Detect recurring issue clusters.
    """

    def detect(
        self,
        summaries: List[ClusterSummary]
    ) -> List[RecurrenceResult]:

        logger.info("Starting recurrence detection...")

        results: List[RecurrenceResult] = []

        for summary in summaries:

            recurrence_score = 0

            # Weighted score based on priority distribution
            for priority, count in summary.priority_distribution.items():

                weight = PRIORITY_WEIGHTS.get(priority.upper(), 1)

                recurrence_score += count * weight

            problem_candidate = (
                recurrence_score >=
                PROBLEM_CANDIDATE_THRESHOLD
            )

            recommendation = (
                "Recommend Problem Record Creation"
                if problem_candidate
                else
                "Continue Monitoring"
            )

            results.append(

                RecurrenceResult(

                    cluster_summary=summary,

                    recurrence_score=round(
                        recurrence_score,
                        2
                    ),

                    problem_candidate=problem_candidate,

                    recommendation=recommendation

                )

            )

        logger.info(
            "Generated recurrence results for %d clusters.",
            len(results)
        )

        return results