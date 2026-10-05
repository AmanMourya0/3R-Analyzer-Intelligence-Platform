"""
Core exceptions for the 3R Analyzer Intelligence application.
"""

class JobCancelledException(Exception):
    def __init__(self, message: str = "Job was cancelled.", reason: str = "USER_REQUESTED"):
        super().__init__(message)
        self.reason = reason
