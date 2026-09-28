import pytest
from unittest.mock import MagicMock
from app.services.process_service import ProcessService
from app.pipelines.incident_pipeline import IncidentPipeline
from app.repositories.job_repository import JobRepository
from app.constants import JOB_STATUS_PENDING, JOB_STATUS_FAILED, JOB_STATUS_RUNNING
from app.database.processing_job_model import ProcessingJob

def test_database_exception_during_processing_rolls_back_and_marks_failed(monkeypatch, db_session, sqlite_session_factory):
    monkeypatch.setattr("app.services.process_service.SessionLocal", sqlite_session_factory)
    # Setup a pending job in DB
    job = ProcessingJob(
        dataset_path="dummy.csv",
        source_type="upload",
        status=JOB_STATUS_PENDING,
        message="Queued"
    )
    db_session.add(job)
    db_session.commit()
    
    pipeline = IncidentPipeline()
    process_service = ProcessService(pipeline)
    
    # Mock ProcessService._update_job_progress to raise an Exception simulating DB failure during processing
    def mock_update(*args, **kwargs):
        if args[2] == "STARTING":
            return # Let the first status update pass to mark RUNNING
        raise Exception("Simulated DB Failure")
    
    monkeypatch.setattr(process_service, "_update_job_progress", mock_update)
    
    # Run process_job
    process_service.process_job(job.id)
    
    # Assert
    db_session.refresh(job)
    assert job.status == JOB_STATUS_FAILED
    assert "Simulated DB Failure" in job.error_message
    
def test_concurrent_job_is_rejected(db_session, monkeypatch, sqlite_session_factory):
    monkeypatch.setattr("app.services.process_service.SessionLocal", sqlite_session_factory)
    # Setup two jobs. One RUNNING, one PENDING.
    job1 = ProcessingJob(
        dataset_path="dummy1.csv",
        status=JOB_STATUS_RUNNING,
    )
    job2 = ProcessingJob(
        dataset_path="dummy2.csv",
        status=JOB_STATUS_PENDING,
    )
    db_session.add_all([job1, job2])
    db_session.commit()
    
    process_service = ProcessService(IncidentPipeline())
    
    process_service.process_job(job2.id)
    
    db_session.refresh(job2)
    assert job2.status == JOB_STATUS_FAILED
    assert "Another AI clustering job is currently active." in job2.error_message

def test_dataset_loading_failure(monkeypatch, db_session, sqlite_session_factory):
    monkeypatch.setattr("app.services.process_service.SessionLocal", sqlite_session_factory)
    job = ProcessingJob(
        dataset_path="does_not_exist.csv",
        status=JOB_STATUS_PENDING,
    )
    db_session.add(job)
    db_session.commit()
    
    process_service = ProcessService(IncidentPipeline())
    
    process_service.process_job(job.id)
    
    db_session.refresh(job)
    assert job.status == JOB_STATUS_FAILED
    # It should fail because file does not exist, and correctly rollback and mark failed.
