import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import engine, SessionLocal
from app.database.base import Base
from app.database.processing_job_model import ProcessingJob
from app.constants import JOB_STATUS_QUEUED, JOB_STATUS_RUNNING, JOB_STATUS_COMPLETED, JOB_STATUS_FAILED, JOB_STATUS_CANCELLED, JOB_STATUS_PENDING
from app.services.process_service import ProcessService, JobCancelledException
from app.repositories.job_repository import JobRepository
from app.pipelines.incident_pipeline import IncidentPipeline

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    Base.metadata.create_all(bind=engine)
    yield
    session = SessionLocal()
    session.query(ProcessingJob).delete()
    session.commit()
    session.close()

def create_mock_job(session, status=JOB_STATUS_PENDING):
    job = ProcessingJob(
        dataset_path="dummy.csv",
        source_type="upload",
        status=status,
        progress_stage=status,
        progress_message="test",
        progress_percent=0
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job

def test_cancel_queued_job():
    session = SessionLocal()
    job = create_mock_job(session, JOB_STATUS_PENDING)
    session.close()

    response = client.post(f"/jobs/{job.id}/cancel")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == JOB_STATUS_CANCELLED

def test_cancel_running_job():
    session = SessionLocal()
    job = create_mock_job(session, JOB_STATUS_RUNNING)
    session.close()

    response = client.post(f"/jobs/{job.id}/cancel")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == JOB_STATUS_CANCELLED

def test_reject_cancellation_of_completed_job():
    session = SessionLocal()
    job = create_mock_job(session, JOB_STATUS_COMPLETED)
    session.close()

    response = client.post(f"/jobs/{job.id}/cancel")
    assert response.status_code == 400
    data = response.json()
    assert "Cannot cancel" in data["detail"]

def test_reject_cancellation_of_failed_job():
    session = SessionLocal()
    job = create_mock_job(session, JOB_STATUS_FAILED)
    session.close()

    response = client.post(f"/jobs/{job.id}/cancel")
    assert response.status_code == 400

def test_idempotent_repeated_cancellation():
    session = SessionLocal()
    job = create_mock_job(session, JOB_STATUS_PENDING)
    session.close()

    response1 = client.post(f"/jobs/{job.id}/cancel")
    assert response1.status_code == 200
    
    response2 = client.post(f"/jobs/{job.id}/cancel")
    assert response2.status_code == 200
    assert response2.json()["status"] == JOB_STATUS_CANCELLED

def test_cancellation_during_pipeline_checkpoint():
    session = SessionLocal()
    job = create_mock_job(session, JOB_STATUS_RUNNING)
    
    pipeline_mock = MagicMock(spec=IncidentPipeline)
    service = ProcessService(pipeline=pipeline_mock)
    
    # Mark it as cancelled in DB
    job.status = JOB_STATUS_CANCELLED
    session.commit()
    
    with pytest.raises(JobCancelledException):
        service._update_job_progress(session, job, "TEST_STAGE", "testing", 50)
        
    session.close()
