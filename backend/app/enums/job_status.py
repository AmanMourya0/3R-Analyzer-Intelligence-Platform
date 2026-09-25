"""
Job Status Enumeration

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from enum import Enum


class JobStatus(str, Enum):
    """
    Processing Job Status.
    """

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"