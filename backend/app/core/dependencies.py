"""
Application Dependencies

Creates reusable application services.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from __future__ import annotations

from app.pipelines.incident_pipeline import IncidentPipeline

from app.services.job_service import JobService
from app.services.process_service import ProcessService
from app.services.scheduler_service import SchedulerService
from app.database.database import SessionLocal
from app.services.dashboard_service import DashboardService

# ==========================================================
# Singleton Instances
# ==========================================================

_dashboard_service: DashboardService | None = None
_process_service: ProcessService | None = None
_scheduler_service: SchedulerService | None = None
_job_service: JobService | None = None


# ==========================================================
# Dependency Providers
# ==========================================================

def get_process_service() -> ProcessService:
    """
    Return singleton ProcessService instance.
    """

    global _process_service

    if _process_service is None:

        pipeline = IncidentPipeline()

        _process_service = ProcessService(
            pipeline
        )

    return _process_service


def get_scheduler_service() -> SchedulerService:
    """
    Return singleton SchedulerService instance.
    """

    global _scheduler_service

    if _scheduler_service is None:

        _scheduler_service = SchedulerService(
            get_process_service()
        )

    return _scheduler_service


def get_job_service() -> JobService:
    """
    Return singleton JobService instance.
    """

    global _job_service

    if _job_service is None:

        _job_service = JobService(
            get_scheduler_service()
        )

    return _job_service



#/////////////////////////////////////////

def get_dashboard_service():

    global _dashboard_service

    if _dashboard_service is None:

        session = SessionLocal()

        _dashboard_service = DashboardService(
            session
        )

    return _dashboard_service