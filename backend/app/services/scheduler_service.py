"""
Scheduler service for asynchronous processing jobs.
"""

from datetime import datetime
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.services.process_service import ProcessService
from app.utils.logger import logger


class SchedulerService:
    """
    Thin wrapper around APScheduler job scheduling.
    """

    def __init__(
        self,
        process_service: ProcessService
    ) -> None:
        """
        Initialize and start the background scheduler.

        The scheduler is created but NOT started.
        FastAPI lifespan is responsible for starting it.
        """

        self.process_service = process_service
        self._enrichment_service = None
        self.scheduler = BackgroundScheduler(
            timezone="UTC"
        )

    @property
    def enrichment_service(self):
        """Lazily initialize EnrichmentService to avoid KeyBERT import at startup."""
        if self._enrichment_service is None:
            from app.services.enrichment_service import EnrichmentService
            self._enrichment_service = EnrichmentService()
        return self._enrichment_service

    def start(self) -> None:
        """
        Start APScheduler if it is not already running.
        """

        if not self.scheduler.running:

            self.scheduler.start()

            logger.info(
                "APScheduler started."
            )

    def shutdown(self) -> None:
        """
        Shutdown APScheduler.
        """

        from app.database.database import SessionLocal
        from app.database.processing_job_model import ProcessingJob
        from app.constants import JOB_STATUS_RUNNING, JOB_STATUS_CANCELLED

        session = SessionLocal()
        try:
            active_jobs = session.query(ProcessingJob).filter(ProcessingJob.status == JOB_STATUS_RUNNING).all()
            for job in active_jobs:
                logger.info("Cancelling active job %s due to server shutdown.", job.id)
                job.status = JOB_STATUS_CANCELLED
                job.message = "Processing cancelled due to server shutdown."
                job.progress_stage = "CANCELLED"
                job.progress_message = "Server shutdown."
            session.commit()
        except Exception as e:
            logger.error("Failed to cancel active jobs on shutdown: %s", e)
        finally:
            session.close()

        if self.scheduler.running:

            self.scheduler.shutdown(
                wait=False
            )

            logger.info(
                "APScheduler stopped."
            )

    def schedule_processing_job(
        self,
        job_id: str
    ) -> None:
        """
        Schedule a processing job for background execution.
        """

        self.scheduler.add_job(
            func=self.process_service.process_job,
            trigger="date",
            run_date=datetime.utcnow() + timedelta(seconds=1),
            args=[job_id],
            id=f"processing-job-{job_id}",
            replace_existing=True,
        )

        logger.info(
            "Scheduled processing job %s.",
            job_id
        )

    def schedule_enrichment_job(
        self,
        job_id: str
    ) -> None:
        """
        Schedule an AI cluster naming enrichment job for background execution.
        """

        self.scheduler.add_job(
            func=self.enrichment_service.process_enrichment_job,
            trigger="date",
            run_date=datetime.utcnow() + timedelta(seconds=1),
            args=[job_id],
            id=f"enrichment-job-{job_id}",
            replace_existing=True,
        )

        logger.info(
            "Scheduled enrichment job %s.",
            job_id
        )

