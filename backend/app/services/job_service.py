"""
Application service for processing job lifecycle operations.
"""

from typing import List
from typing import Optional
from datetime import date

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.processing_job_model import ProcessingJob
from app.repositories.job_repository import JobRepository
from app.services.scheduler_service import SchedulerService
from app.utils.logger import logger


SERVICENOW_DEMO_DATASET = "dataset/Dummy_Incident_Dataset_V2_5000.xlsx"


class JobService:
    """
    Coordinates processing job persistence and scheduling.
    """

    def __init__(
        self,
        scheduler_service: SchedulerService
    ) -> None:
        """
        Initialize the service.
        """

        self.scheduler_service = scheduler_service

    def create_processing_job(
        self,
        dataset_path: str,
        source_type: str = "upload",
        assignment_groups: Optional[List[str]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> ProcessingJob:
        """
        Create a queued processing job and schedule background execution.
        """

        session: Session = SessionLocal()

        try:

            repository = JobRepository(
                session
            )

            resolved_dataset_path = (
                SERVICENOW_DEMO_DATASET
                if source_type == "servicenow"
                else dataset_path
            )

            job = repository.create(
                resolved_dataset_path,
                source_type=source_type,
                assignment_groups=assignment_groups,
                start_date=start_date,
                end_date=end_date,
            )

            session.commit()
            session.refresh(
                job
            )

            self.scheduler_service.schedule_processing_job(
                job.id
            )

            logger.info(
                "Created processing job %s.",
                job.id
            )

            session.expunge(
                job
            )

            return job

        except Exception:

            session.rollback()

            logger.exception(
                "Unable to create processing job."
            )

            raise

        finally:

            session.close()


    def list_jobs(self) -> List[ProcessingJob]:
        """
        Return all processing jobs.
        """

        session: Session = SessionLocal()

        try:

            return JobRepository(
                session
            ).list_all()

        except Exception:

            logger.exception(
                "Unable to list processing jobs."
            )

            raise

        finally:

            session.close()

    def list_jobs_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None
    ) -> tuple[List[ProcessingJob], int, int]:
        """
        Return paginated processing jobs.
        """

        session: Session = SessionLocal()

        try:

            return JobRepository(
                session
            ).list_jobs_paginated(page=page, page_size=page_size, status=status)

        except Exception:

            logger.exception(
                "Unable to list paginated processing jobs."
            )

            raise

        finally:

            session.close()

    def get_job(
        self,
        job_id: str
    ) -> Optional[ProcessingJob]:
        """
        Return one processing job by UUID string.
        """

        session: Session = SessionLocal()

        try:

            return JobRepository(
                session
            ).get_by_id(
                job_id
            )

        except Exception:

            logger.exception(
                "Unable to fetch processing job %s.",
                job_id
            )

            raise

        finally:

            session.close()
