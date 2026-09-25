"""
Incident Processing Service

Coordinates loading, AI processing and persistence layer.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

import time
import json

import pandas as pd

from sqlalchemy.orm import Session

from app.enums import JobStatus
from app.database.database import SessionLocal

from app.services.incident_loader import IncidentLoader

from app.pipelines.incident_pipeline import (
    IncidentPipeline
)

from app.repositories.incident_repository import (
    IncidentRepository
)

from app.repositories.cluster_repository import (
    ClusterRepository
)

from app.repositories.job_repository import (
    JobRepository
)

from app.repositories.recurrence_repository import (
    RecurrenceRepository
)

from app.models.pipeline_result import (
    PipelineResult
)
from app.services.performance.stage_timer import stage_timer

from app.utils.logger import logger
from app.constants import ASSIGNMENT_GROUP, CREATED_DATE
from app.services.preprocessing import Preprocessor


class ProcessService:

    def __init__(
        self,
        pipeline: IncidentPipeline
    ):

        self.pipeline = pipeline

    # ==========================================================
    # Progress
    # ==========================================================

    def _update_job_progress(
        self,
        session: Session,
        job,
        stage: str,
        message: str,
        percent: int
    ) -> None:

        repository = JobRepository(
            session
        )

        repository.update_progress(
            job,
            progress_stage=stage,
            progress_message=message,
            progress_percent=percent
        )

        session.commit()

        logger.info(
            "Job %s progress: %s - %s (%d%%)",
            job.id,
            stage,
            message,
            percent
        )

    # ==========================================================
    # Dataset Processing
    # ==========================================================

    def _apply_processing_scope(self, dataframe: pd.DataFrame, job) -> pd.DataFrame:
        """Filter the source dataset before it enters the AI pipeline."""

        scoped = dataframe.rename(columns=Preprocessor.COLUMN_MAPPING).copy()
        groups = json.loads(job.assignment_groups) if job.assignment_groups else []
        groups = [group for group in groups if group.strip().lower() != "all"]

        if groups:
            if ASSIGNMENT_GROUP not in scoped.columns:
                raise ValueError("The dataset does not contain an Assignment Group column.")
            scoped = scoped[scoped[ASSIGNMENT_GROUP].isin(groups)]

        if job.start_date or job.end_date:
            if CREATED_DATE not in scoped.columns:
                raise ValueError("The dataset does not contain a Created Date column.")
            dates = pd.to_datetime(scoped[CREATED_DATE], errors="coerce")
            if job.start_date:
                scoped = scoped[dates >= pd.Timestamp(job.start_date)]
                dates = pd.to_datetime(scoped[CREATED_DATE], errors="coerce")
            if job.end_date:
                scoped = scoped[dates <= pd.Timestamp(job.end_date)]

        if scoped.empty:
            raise ValueError("No incidents matched the selected processing scope.")

        return scoped

    def process_dataset(
        self,
        session: Session,
        job,
        dataset_path: str
    ) -> PipelineResult:
        """
        Execute the complete AI pipeline and persist the
        latest analytical snapshot.

        The supplied session and job are owned by process_job().
        """

        logger.info("=" * 80)
        logger.info(
            "Starting incident processing..."
        )
        logger.info(
            "Dataset : %s",
            dataset_path
        )

        # --------------------------------------------------
        # Loading
        # --------------------------------------------------

        self._update_job_progress(
            session,
            job,
            "LOADING_DATA",
            "Loading incident dataset...",
            10
        )

        loader = IncidentLoader(
            dataset_path
        )

        dataframe = loader.load()

        self._update_job_progress(
            session,
            job,
            "APPLYING_SCOPE",
            "Applying assignment group and date range scope...",
            12
        )

        dataframe = self._apply_processing_scope(dataframe, job)

        logger.info(
            "Loaded %d incidents.",
            len(dataframe)
        )

        # --------------------------------------------------
        # Pipeline callback
        # --------------------------------------------------

        def progress_callback(
            stage: str,
            message: str,
            percent: int
        ) -> None:

            self._update_job_progress(
                session,
                job,
                stage,
                message,
                percent
            )

        # --------------------------------------------------
        # AI Pipeline
        # --------------------------------------------------

        result = self.pipeline.run(
            dataframe,
            progress_callback=progress_callback
        )

        # --------------------------------------------------
        # Repositories
        # --------------------------------------------------

        incident_repository = (
            IncidentRepository(session)
        )

        cluster_repository = (
            ClusterRepository(session)
        )

        recurrence_repository = (
            RecurrenceRepository(session)
        )

        # --------------------------------------------------
        # Persistence
        # --------------------------------------------------

        self._update_job_progress(
            session,
            job,
            "PERSISTING_RESULTS",
            "Saving AI analysis results...",
            92
        )

        logger.info(
            "Clearing previous analytical results..."
        )

        recurrence_repository.delete_all()

        incident_repository.delete_all()

        cluster_repository.delete_all()

        session.flush()

        logger.info(
            "Persisting latest analytical snapshot..."
        )

        cluster_repository.save(
            result.cluster_summaries
        )

        incident_repository.save(
            result.dataframe
        )

        recurrence_repository.save(
            result.recurrence_results
        )

        session.commit()

        logger.info("=" * 80)
        logger.info(
            "Processing completed successfully."
        )

        logger.info(
            "Incidents : %d",
            len(result.dataframe)
        )

        logger.info(
            "Clusters : %d",
            len(result.cluster_summaries)
        )

        return result

    # ==========================================================
    # Job Processing
    # ==========================================================

    def process_job(
        self,
        job_id: str
    ) -> None:
        """
        Process a queued job and update its PostgreSQL status.
        """

        session: Session = SessionLocal()

        repository = JobRepository(
            session
        )

        try:

            # --------------------------------------------------
            # Fetch Job
            # --------------------------------------------------

            job = repository.get_by_id(
                job_id
            )

            if job is None:

                logger.error(
                    "Processing job %s was not found.",
                    job_id
                )

                return

            if job.status == JobStatus.RUNNING.value:

                logger.info(
                    "Processing job %s is already running.",
                    job_id
                )

                return

            # --------------------------------------------------
            # Mark Running
            # --------------------------------------------------

            repository.mark_running(
                job
            )

            session.commit()

            self._update_job_progress(
                session,
                job,
                "STARTING",
                "Starting incident intelligence processing...",
                5
            )

            start_time = time.perf_counter()

            # --------------------------------------------------
            # Execute Processing
            # --------------------------------------------------

            result = self.process_dataset(
                session,
                job,
                job.dataset_path
            )

            processing_time = round(
                time.perf_counter()
                - start_time,
                2
            )

            # --------------------------------------------------
            # Mark Completed
            # --------------------------------------------------

            repository.mark_completed(
                job,
                processing_time_seconds=processing_time,
                total_incidents=len(
                    result.dataframe
                ),
                total_clusters=len(
                    result.cluster_summaries
                ),
                total_problem_candidates=sum(
                    item.problem_candidate
                    for item in result.recurrence_results
                ),
                total_runners=result.three_r_summary.runner_count if result.three_r_summary else 0,
                total_repeaters=result.three_r_summary.repeater_count if result.three_r_summary else 0,
                total_rares=result.three_r_summary.rare_count if result.three_r_summary else 0
            )

            # --------------------------------------------------
            # Final Progress
            # --------------------------------------------------

            repository.update_progress(
                job,
                progress_stage="COMPLETED",
                progress_message=(
                    "Incident intelligence analysis completed."
                ),
                progress_percent=100
            )

            session.commit()

            logger.info(
                "Processing job %s completed successfully.",
                job_id
            )

        except Exception as ex:

            logger.exception(
                "Processing job %s failed.",
                job_id
            )

            session.rollback()

            # --------------------------------------------------
            # Mark Failed
            # --------------------------------------------------

            try:

                job = repository.get_by_id(
                    job_id
                )

                if job is not None:

                    repository.mark_failed(
                        job,
                        str(ex)
                    )

                    repository.update_progress(
                        job,
                        progress_stage="FAILED",
                        progress_message=(
                            "Incident processing failed."
                        ),
                        progress_percent=(
                            job.progress_percent
                            if job.progress_percent is not None
                            else 0
                        )
                    )

                    session.commit()

            except Exception:

                session.rollback()

                logger.exception(
                    "Unable to mark processing job %s as failed.",
                    job_id
                )

        finally:

            session.close()
