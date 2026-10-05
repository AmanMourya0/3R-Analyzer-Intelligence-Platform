import pytest
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.database.database import SessionLocal, engine
from app.database.base import Base
from app.database.processing_job_model import ProcessingJob
from app.constants import (
    JOB_TYPE_PROCESSING,
    JOB_TYPE_AI_CLUSTER_NAMING,
    JOB_STATUS_RUNNING,
    JOB_STATUS_COMPLETED,
    JOB_STATUS_CANCELLED,
    JOB_STATUS_FAILED
)
from app.main import app

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    pass

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        # Clean jobs
        session.query(ProcessingJob).delete()
        session.commit()
        yield session
    finally:
        session.close()

def create_job(session: Session, job_type: str, status: str, progress_percent: int):
    job = ProcessingJob(
        job_type=job_type,
        status=status,
        progress_percent=progress_percent,
        dataset_path="dummy.csv",
        source_type="upload"
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job

def test_api_status_returns_running_processing_over_completed_ai(db_session):
    """TEST A & TEST B: /api/status returns active PROCESSING, ignores COMPLETED AI job."""
    # Create RUNNING processing job
    proc_job = create_job(db_session, JOB_TYPE_PROCESSING, JOB_STATUS_RUNNING, 30)
    
    # Create COMPLETED AI job after processing job
    ai_job = create_job(db_session, JOB_TYPE_AI_CLUSTER_NAMING, JOB_STATUS_COMPLETED, 100)
    
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "processing"
    assert data["job_id"] == str(proc_job.id)
    assert data["percent"] == 30

def test_api_status_returns_latest_completed_processing_if_none_active(db_session):
    """TEST C: /api/status returns COMPLETED processing, ignores newer AI job."""
    proc_job = create_job(db_session, JOB_TYPE_PROCESSING, JOB_STATUS_COMPLETED, 100)
    ai_job = create_job(db_session, JOB_TYPE_AI_CLUSTER_NAMING, JOB_STATUS_COMPLETED, 100)
    
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "done"
    assert data["job_id"] == str(proc_job.id)
    assert data["percent"] == 100

def test_api_status_defensive_percent_for_running(db_session):
    """TEST E: RUNNING job never exposes 100%."""
    proc_job = create_job(db_session, JOB_TYPE_PROCESSING, JOB_STATUS_RUNNING, 100)
    
    response = client.get("/api/status")
    data = response.json()
    
    assert data["status"] == "processing"
    assert data["percent"] == 99  # Should be capped

def test_enrichment_status_422_fix():
    """TEST H: No active enrichment job -> valid response, not 422."""
    response = client.get("/api/clusters/enrichment-status")
    assert response.status_code == 200
    assert "naming_status" in response.json()
    
def test_job_progress_cannot_regress(db_session):
    """TEST F: Progress cannot regress (via JobRepository / ProcessService logic)."""
    # Just testing the ProcessService logic directly
    from app.services.process_service import ProcessService
    from app.pipelines.incident_pipeline import IncidentPipeline
    
    ps = ProcessService(pipeline=IncidentPipeline())
    job = create_job(db_session, JOB_TYPE_PROCESSING, JOB_STATUS_RUNNING, 90)
    
    # Update to 95
    ps._update_job_progress(db_session, job, "PERSISTING_RESULTS", "msg", 95)
    db_session.refresh(job)
    assert job.progress_percent == 95
    
    # Attempt to update to 92 (should stay 95)
    ps._update_job_progress(db_session, job, "SOME_OTHER_STAGE", "msg", 92)
    db_session.refresh(job)
    assert job.progress_percent == 95
    
    # Finish to COMPLETED at 100
    ps._update_job_progress(db_session, job, "COMPLETED", "msg", 100)
    db_session.refresh(job)
    assert job.progress_percent == 100

def test_cancellation_behavior(db_session):
    """TEST D & Cancellation: RUNNING job cancelled properly."""
    proc_job = create_job(db_session, JOB_TYPE_PROCESSING, JOB_STATUS_RUNNING, 30)
    
    # Cancel it
    response = client.post(f"/api/jobs/{proc_job.id}/cancel")
    assert response.status_code == 200
    
    # Verify /api/status returns cancelled
    response = client.get("/api/status")
    data = response.json()
    assert data["status"] == "cancelled"
    assert data["job_id"] == str(proc_job.id)

    # Verify AI enrichment job is unaffected by this specific cancellation
    ai_job = create_job(db_session, JOB_TYPE_AI_CLUSTER_NAMING, JOB_STATUS_RUNNING, 30)
    
    # Check AI status
    response = client.get("/api/clusters/enrichment-status")
    data = response.json()
    assert data["naming_status"] == "AI_ENRICHMENT_RUNNING"
    assert data["job"]["status"] == "RUNNING"


def test_enrichment_status_resets_for_new_dataset(db_session):
    """Test that a new PROCESSING job resets the enrichment status to STANDARD."""
    import time

    # 1. Process Dataset A (older)
    create_job(db_session, JOB_TYPE_PROCESSING, JOB_STATUS_COMPLETED, 100)
    time.sleep(0.01)

    # 2. Enrich Dataset A (newer than Dataset A's processing)
    create_job(db_session, JOB_TYPE_AI_CLUSTER_NAMING, JOB_STATUS_COMPLETED, 100)
    
    # Enrichment status should be AI_ENRICHED
    response = client.get("/api/clusters/enrichment-status")
    assert response.json()["naming_status"] == "AI_ENRICHED"
    
    time.sleep(0.01)

    # 3. Process Dataset B (newest)
    create_job(db_session, JOB_TYPE_PROCESSING, JOB_STATUS_COMPLETED, 100)
    
    # Enrichment status should now reset to STANDARD because the dataset is new
    response = client.get("/api/clusters/enrichment-status")
    assert response.json()["naming_status"] == "STANDARD"
