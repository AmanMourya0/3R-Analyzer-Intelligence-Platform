"""
Processing job repository.

Owns persistence operations for asynchronous processing job records.
"""

from datetime import datetime
import json
from typing import Optional
from typing import List

from sqlalchemy.orm import Session

from app.constants import (
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
)
from app.database.processing_job_model import ProcessingJob
from app.repositories.repository_interface import RepositoryInterface


class JobRepository(RepositoryInterface):
    """
    Repository responsible for ProcessingJob persistence.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, data: ProcessingJob) -> None:
        """
        Persist a processing job instance.
        """

        self.session.add(data)

    def create(
        self,
        dataset_path: str,
        source_type: str = "upload",
        assignment_groups: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> ProcessingJob:
        """
        Create a pending processing job.
        """

        job = ProcessingJob(
            dataset_path=dataset_path,
            source_type=source_type,
            assignment_groups=json.dumps(assignment_groups) if assignment_groups else None,
            start_date=start_date,
            end_date=end_date,
            status=JOB_STATUS_PENDING,
            message="Processing job queued.",
            progress_stage="QUEUED",
            progress_message="Processing job queued.",
            progress_percent=0,
        )

        self.save(job)
        self.session.flush()

        return job
    
    def update_progress(self, job, progress_stage: str, progress_message: str, progress_percent: int) -> None:
        """
        Update the progress of a processing job.
        """

        job.progress_stage = progress_stage

        job.progress_message = progress_message

        job.progress_percent = int(progress_percent)

        self.session.flush()


    def get_by_id(self, job_id: str) -> Optional[ProcessingJob]:
        """
        Return one processing job by UUID string.
        """

        return (
            self.session.query(ProcessingJob)
            .filter(ProcessingJob.id == job_id)
            .one_or_none()
        )

    def list_all(self) -> List[ProcessingJob]:
        """
        Return processing jobs ordered newest first.
        """

        return (
            self.session.query(ProcessingJob)
            .order_by(ProcessingJob.created_at.desc())
            .all()
        )

    def list_jobs_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None
    ) -> tuple[List[ProcessingJob], int, int]:
        """
        Return paginated processing jobs ordered newest first.
        """
        import math

        query = self.session.query(ProcessingJob)
        if status:
            query = query.filter(ProcessingJob.status == status)

        total = query.count()
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        jobs = (
            query
            .order_by(ProcessingJob.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return jobs, total, total_pages

    def mark_running(self, job: ProcessingJob) -> None:
        """
        Mark a job as running.
        """

        job.status = JOB_STATUS_RUNNING
        job.message = "Processing job running."
        job.started_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

    def mark_completed(
        self,
        job: ProcessingJob,
        processing_time_seconds: float,
        total_incidents: int,
        total_clusters: int,
        total_problem_candidates: int,
        total_runners: int = 0,
        total_repeaters: int = 0,
        total_rares: int = 0
    ) -> None:
        """
        Mark a job as completed with processing metrics.
        """

        job.status = JOB_STATUS_COMPLETED
        job.message = "Dataset processed successfully."
        job.processing_time_seconds = float(processing_time_seconds)
        job.total_incidents = int(total_incidents)
        job.total_clusters = int(total_clusters)
        job.total_problem_candidates = int(total_problem_candidates)
        job.total_runners = int(total_runners)
        job.total_repeaters = int(total_repeaters)
        job.total_rares = int(total_rares)
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

    def mark_failed(
        self,
        job: ProcessingJob,
        error_message: str
    ) -> None:
        """
        Mark a job as failed.
        """

        job.status = JOB_STATUS_FAILED
        job.message = "Dataset processing failed."
        job.error_message = error_message
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()
