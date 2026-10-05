"""
AI Cluster Name Enrichment Service

Runs KeyBERT-based cluster naming as an optional asynchronous operation
AFTER the core 3R pipeline has completed.

This service:
- Reads existing cluster data from PostgreSQL
- Retrieves incident texts for each cluster
- Runs AIClusterNamer (KeyBERT) to generate improved names
- Updates ONLY cluster names — no other analytical data is modified
- Supports cancellation, progress tracking, and failure safety

INVARIANT: This operation must NEVER modify cluster IDs, cluster membership,
recurrence scores, 3R classifications, or any other analytical results.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

import time
import logging
from typing import Dict, List

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import SessionLocal
from app.database.cluster_model import Cluster
from app.database.incident_model import Incident
from app.database.processing_job_model import ProcessingJob
from app.repositories.job_repository import JobRepository
from app.clustering.cluster_namer import AIClusterNamer
from app.constants import (
    JOB_STATUS_CANCELLED,
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
    JOB_STATUS_PENDING,
    JOB_STATUS_RUNNING,
    JOB_TYPE_AI_CLUSTER_NAMING,
    NAMING_STATUS_AI_ENRICHED,
    NAMING_STATUS_STANDARD,
)

logger = logging.getLogger(__name__)


class EnrichmentService:
    """
    Manages AI cluster name enrichment as a separate, non-blocking operation.
    """

    def process_enrichment_job(self, job_id: str) -> None:
        """
        Execute the AI cluster naming enrichment job.

        This method:
        1. Validates preconditions (clusters exist, no active processing)
        2. Retrieves cluster texts from the database
        3. Runs KeyBERT via AIClusterNamer
        4. Updates cluster names atomically (all or nothing)
        5. Updates job status throughout

        Failure at any point preserves existing standard cluster names.
        """
        session: Session = SessionLocal()
        repository = JobRepository(session)

        try:
            # --------------------------------------------------
            # Fetch job
            # --------------------------------------------------
            job = repository.get_by_id(job_id)
            if job is None:
                logger.error("Enrichment job %s not found.", job_id)
                return

            if job.status == JOB_STATUS_RUNNING:
                logger.info("Enrichment job %s is already running.", job_id)
                return

            # Check for duplicate running enrichment
            if repository.has_running_enrichment_job():
                logger.warning("Another enrichment job is already running. Failing job %s.", job_id)
                repository.mark_failed(job, "AI cluster-name enrichment is already running.")
                session.commit()
                return

            # Check for active processing jobs
            if repository.has_running_job():
                # Check if the running job is a different processing job
                running_jobs = (
                    session.query(ProcessingJob)
                    .filter(
                        ProcessingJob.status == JOB_STATUS_RUNNING,
                        ProcessingJob.job_type != JOB_TYPE_AI_CLUSTER_NAMING,
                    )
                    .count()
                )
                if running_jobs > 0:
                    logger.warning("Dataset processing is active. Failing enrichment job %s.", job_id)
                    repository.mark_failed(
                        job,
                        "AI cluster-name enrichment can start only after dataset processing is complete."
                    )
                    session.commit()
                    return

            # --------------------------------------------------
            # Mark running
            # --------------------------------------------------
            repository.mark_running(job)
            session.commit()

            repository.update_progress(
                job,
                progress_stage="STARTING",
                progress_message="Starting AI cluster name enrichment...",
                progress_percent=5,
            )
            session.commit()

            start_time = time.perf_counter()

            # --------------------------------------------------
            # Validate: clusters exist
            # --------------------------------------------------
            cluster_count = session.query(func.count(Cluster.cluster_id)).scalar() or 0
            if cluster_count == 0:
                repository.mark_failed(
                    job,
                    "No processed dataset is available for AI cluster-name enrichment."
                )
                session.commit()
                return

            repository.update_progress(
                job,
                progress_stage="LOADING_CLUSTERS",
                progress_message=f"Loading {cluster_count} clusters...",
                progress_percent=10,
            )
            session.commit()

            # --------------------------------------------------
            # Retrieve cluster texts
            # --------------------------------------------------
            clusters = session.query(Cluster).order_by(Cluster.cluster_id).all()

            cluster_texts: Dict[int, List[str]] = {}
            for cluster in clusters:
                # Get combined_text (short_description + description) for incidents in this cluster
                incident_texts = (
                    session.query(Incident.short_description, Incident.description)
                    .filter(Incident.cluster_id == cluster.cluster_id)
                    .limit(50)
                    .all()
                )
                texts = []
                for short_desc, desc in incident_texts:
                    parts = []
                    if short_desc:
                        parts.append(str(short_desc))
                    if desc:
                        parts.append(str(desc))
                    if parts:
                        texts.append(" ".join(parts))
                if texts:
                    cluster_texts[cluster.cluster_id] = texts

            repository.update_progress(
                job,
                progress_stage="AI_NAMING",
                progress_message="Running KeyBERT AI cluster naming...",
                progress_percent=25,
            )
            session.commit()

            # --------------------------------------------------
            # Cancellation check
            # --------------------------------------------------
            def is_cancelled() -> bool:
                session.refresh(job)
                return job.status == JOB_STATUS_CANCELLED

            # --------------------------------------------------
            # Run AIClusterNamer (KeyBERT)
            # --------------------------------------------------
            ai_namer = AIClusterNamer()

            if not ai_namer.is_available:
                repository.mark_failed(
                    job,
                    "AI cluster naming dependency (KeyBERT) is unavailable. "
                    "Please ensure keybert is installed."
                )
                session.commit()
                return

            try:
                ai_names = ai_namer.generate_ai_names(
                    cluster_texts=cluster_texts,
                    cancelled_check=is_cancelled,
                )
            except RuntimeError as exc:
                repository.mark_failed(job, str(exc))
                session.commit()
                return

            # Check if cancelled during naming
            if is_cancelled():
                logger.info("Enrichment job %s was cancelled during AI naming.", job_id)
                return

            if not ai_names:
                repository.mark_failed(
                    job,
                    "AI naming produced no results."
                )
                session.commit()
                return

            # --------------------------------------------------
            # Update cluster names atomically
            # --------------------------------------------------
            repository.update_progress(
                job,
                progress_stage="PERSISTING",
                progress_message="Saving AI-enriched cluster names...",
                progress_percent=85,
            )
            session.commit()

            # Generate all names in memory first, then persist
            # This ensures atomicity — either all names update or none
            for cluster in clusters:
                cid = cluster.cluster_id
                if cid in ai_names:
                    # Store original as standard, new as AI-enriched
                    cluster.ai_cluster_name = ai_names[cid]
                    cluster.cluster_name = ai_names[cid]
                    cluster.naming_status = NAMING_STATUS_AI_ENRICHED

            session.commit()

            # --------------------------------------------------
            # Mark completed
            # --------------------------------------------------
            processing_time = round(time.perf_counter() - start_time, 2)

            repository.mark_completed(
                job,
                processing_time_seconds=processing_time,
                total_incidents=0,
                total_clusters=len(ai_names),
                total_problem_candidates=0,
            )

            repository.update_progress(
                job,
                progress_stage="COMPLETED",
                progress_message=f"AI cluster naming completed. {len(ai_names)} clusters enriched.",
                progress_percent=100,
            )

            session.commit()

            logger.info(
                "Enrichment job %s completed. %d clusters enriched in %.2fs.",
                job_id, len(ai_names), processing_time
            )

        except Exception as ex:
            logger.exception("Enrichment job %s failed.", job_id)
            session.rollback()

            try:
                job = repository.get_by_id(job_id)
                if job is not None:
                    repository.mark_failed(job, str(ex))
                    repository.update_progress(
                        job,
                        progress_stage="FAILED",
                        progress_message="AI cluster naming enrichment failed.",
                        progress_percent=job.progress_percent if job.progress_percent else 0,
                    )
                    session.commit()
            except Exception:
                session.rollback()
                logger.exception("Unable to mark enrichment job %s as failed.", job_id)

        finally:
            session.close()
