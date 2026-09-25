"""
Tests for Job Operations (Phase 2.5)
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.database.database import SessionLocal
from app.database.processing_job_model import ProcessingJob

client = TestClient(app)

@pytest.fixture
def mock_job(db_session):
    """
    Creates a mock job in the test database for testing endpoints.
    """
    session = SessionLocal()
    job = ProcessingJob(
        id="test-job-123",
        dataset_path="test_dataset.csv",
        status="COMPLETED",
        progress_stage="FINISHED",
        progress_percent=100,
        total_incidents=100,
        total_clusters=5,
        total_runners=20,
        total_repeaters=80,
        total_rares=0,
        created_at=datetime.utcnow()
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    
    yield job
    
    # Teardown
    session.delete(job)
    session.commit()
    session.close()


def test_list_jobs_paginated(mock_job):
    """
    Test A: GET /api/jobs returns paginated history.
    """
    response = client.get("/api/jobs?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "total" in data
    assert "page" in data
    assert "total_pages" in data
    
    assert data["total"] >= 1
    assert any(j["id"] == "test-job-123" for j in data["jobs"])


def test_get_job_detail(mock_job):
    """
    Test B: GET /api/jobs/{job_id} returns detailed information.
    """
    response = client.get(f"/api/jobs/{mock_job.id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == "test-job-123"
    assert data["total_incidents"] == 100
    assert data["total_runners"] == 20
    assert data["total_repeaters"] == 80


def test_processing_job_invariant(mock_job):
    """
    Test C: Database invariant matches ProcessingJob stats.
    total_incidents == total_runners + total_repeaters + total_rares
    """
    response = client.get(f"/api/jobs/{mock_job.id}")
    data = response.json()
    
    total = data.get("total_incidents", 0)
    runners = data.get("total_runners", 0)
    repeaters = data.get("total_repeaters", 0)
    rares = data.get("total_rares", 0)
    
    assert total == runners + repeaters + rares
