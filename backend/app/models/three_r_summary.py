"""
Domain model representing 3R Classification summary metrics.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from dataclasses import dataclass


@dataclass(slots=True)
class ThreeRSummary:
    """
    Summary metrics for the 3R classification results.
    """

    total: int
    runner_count: int
    repeater_count: int
    rare_count: int
