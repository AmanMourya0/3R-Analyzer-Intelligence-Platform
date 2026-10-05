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

    def cancel_job(
        self,
        job_id: str
    ) -> Optional[ProcessingJob]:
        """
        Cancel a running or queued job safely.
        """
        session: Session = SessionLocal()
        from app.constants import JOB_STATUS_COMPLETED, JOB_STATUS_FAILED, JOB_STATUS_CANCELLED

        try:
            repo = JobRepository(session)
            job = repo.get_by_id(job_id)
            if job is None:
                return None

            if job.status in (JOB_STATUS_COMPLETED, JOB_STATUS_FAILED, JOB_STATUS_CANCELLED):
                # Job is in terminal state, ignore cancellation request idempotently
                return job

            repo.mark_cancelled(job)
            session.commit()
            session.refresh(job)
            
            # Re-fetch after detaching so we can return it safely
            session.expunge(job)
            return job
        except Exception:
            session.rollback()
            logger.exception("Unable to cancel processing job %s.", job_id)
            raise
        finally:
            session.close()

    # ==================================================================
    # AI Enrichment Job Operations
    # ==================================================================

    def create_enrichment_job(self) -> ProcessingJob:
        """
        Create and schedule an AI cluster naming enrichment job.

        Validates:
        - No active processing jobs are running
        - No other enrichment job is currently running
        - Processed data exists in the database
        """
        session: Session = SessionLocal()

        try:
            repo = JobRepository(session)

            # Check for active processing jobs
            from app.constants import JOB_STATUS_RUNNING, JOB_TYPE_AI_CLUSTER_NAMING
            from app.database.cluster_model import Cluster
            from sqlalchemy import func

            active_processing = (
                session.query(ProcessingJob)
                .filter(
                    ProcessingJob.status.in_(["PENDING", JOB_STATUS_RUNNING]),
                    ProcessingJob.job_type != JOB_TYPE_AI_CLUSTER_NAMING,
                )
                .count()
            )
            if active_processing > 0:
                raise ValueError(
                    "AI cluster-name enrichment can start only after dataset processing is complete."
                )

            # Check for running enrichment
            if repo.has_running_enrichment_job():
                raise ValueError(
                    "AI cluster-name enrichment is already running."
                )

            # Check that processed data exists
            cluster_count = session.query(func.count(Cluster.cluster_id)).scalar() or 0
            if cluster_count == 0:
                raise ValueError(
                    "No processed dataset is available for AI cluster-name enrichment."
                )

            job = repo.create_enrichment_job()
            session.commit()
            session.refresh(job)

            self.scheduler_service.schedule_enrichment_job(job.id)

            logger.info("Created enrichment job %s.", job.id)

            session.expunge(job)
            return job

        except ValueError:
            session.rollback()
            raise
        except Exception:
            session.rollback()
            logger.exception("Unable to create enrichment job.")
            raise
        finally:
            session.close()

    def get_enrichment_status(self) -> dict:
        """
        Return the current AI cluster naming enrichment status.

        Returns a dict with:
        - naming_status: STANDARD | AI_ENRICHMENT_RUNNING | AI_ENRICHED | AI_ENRICHMENT_FAILED
        - job: latest enrichment job info or None
        """
        session: Session = SessionLocal()
        try:
            from app.constants import JOB_TYPE_AI_CLUSTER_NAMING
            from app.database.cluster_model import Cluster
            from sqlalchemy import func

            # Find latest enrichment job
            latest_enrichment = (
                session.query(ProcessingJob)
                .filter(ProcessingJob.job_type == JOB_TYPE_AI_CLUSTER_NAMING)
                .order_by(ProcessingJob.created_at.desc())
                .first()
            )

            if latest_enrichment is None:
                return {"naming_status": "STANDARD", "job": None}

            # Find latest completed processing job to define current snapshot identity
            from app.constants import JOB_TYPE_PROCESSING, JOB_STATUS_COMPLETED
            latest_processing = (
                session.query(ProcessingJob)
                .filter(ProcessingJob.job_type == JOB_TYPE_PROCESSING)
                .filter(ProcessingJob.status == JOB_STATUS_COMPLETED)
                .order_by(ProcessingJob.created_at.desc())
                .first()
            )

            # If the latest core dataset snapshot is newer than the latest enrichment job,
            # then the old enrichment no longer applies to the current data.
            if latest_processing and latest_processing.created_at > latest_enrichment.created_at:
                return {"naming_status": "STANDARD", "job": None}

            status = latest_enrichment.status or ""

            if status in ("PENDING", "RUNNING"):
                return {
                    "naming_status": "AI_ENRICHMENT_RUNNING",
                    "job": {
                        "id": str(latest_enrichment.id),
                        "status": status,
                        "progress_stage": latest_enrichment.progress_stage,
                        "progress_message": latest_enrichment.progress_message,
                        "progress_percent": latest_enrichment.progress_percent or 0,
                    },
                }

            if status == "COMPLETED":
                return {
                    "naming_status": "AI_ENRICHED",
                    "job": {
                        "id": str(latest_enrichment.id),
                        "status": status,
                        "progress_stage": latest_enrichment.progress_stage,
                        "progress_message": latest_enrichment.progress_message,
                        "progress_percent": 100,
                        "processing_time_seconds": latest_enrichment.processing_time_seconds,
                        "completed_at": str(latest_enrichment.completed_at) if latest_enrichment.completed_at else None,
                    },
                }

            if status == "FAILED":
                return {
                    "naming_status": "AI_ENRICHMENT_FAILED",
                    "job": {
                        "id": str(latest_enrichment.id),
                        "status": status,
                        "error_message": latest_enrichment.error_message,
                        "progress_stage": latest_enrichment.progress_stage,
                        "progress_message": latest_enrichment.progress_message,
                        "progress_percent": latest_enrichment.progress_percent or 0,
                    },
                }

            return {"naming_status": "STANDARD", "job": None}

        except Exception:
            logger.exception("Unable to get enrichment status.")
            raise
        finally:
            session.close()

