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
        self.scheduler = BackgroundScheduler(
            timezone="UTC"
        )

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
