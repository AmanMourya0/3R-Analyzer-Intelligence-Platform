import pytest
from unittest.mock import patch, MagicMock
from app.services.job_service import JobService
from app.services.scheduler_service import SchedulerService
from app.services.process_service import ProcessService
from app.services.enrichment_service import EnrichmentService
from app.database.database import SessionLocal
from app.database.processing_job_model import ProcessingJob
from app.database.cluster_model import Cluster
from app.database.incident_model import Incident
from app.database.recurrence_model import Recurrence
from app.constants import JOB_TYPE_AI_CLUSTER_NAMING, JOB_STATUS_COMPLETED, JOB_STATUS_FAILED, JOB_STATUS_RUNNING
from sqlalchemy.orm import Session

# =======================================================================
# Test Setup Helpers
# =======================================================================

def clear_db():
    session = SessionLocal()
    session.query(ProcessingJob).delete()
    session.query(Recurrence).delete()
    session.query(Incident).delete()
    session.query(Cluster).delete()
    session.commit()
    session.close()

def seed_cluster_data():
    session = SessionLocal()
    cluster = Cluster(
        cluster_name="Term Frequency Name",
        naming_status="STANDARD",
        incident_count=5,
        three_r_category="RUNNER",
    )
    session.add(cluster)
    session.commit()
    
    incident = Incident(
        incident_number="INC123",
        short_description="Email login failed",
        cluster_id=cluster.cluster_id,
        three_r_category="RUNNER"
    )
    session.add(incident)
    session.commit()
    cluster_id = cluster.cluster_id
    session.close()
    return cluster_id

@pytest.fixture(autouse=True)
def setup_teardown():
    clear_db()
    yield
    clear_db()

# =======================================================================
# Test 1 & 2: Normal Pipeline Tests
# =======================================================================

@patch('app.clustering.cluster_namer.AIClusterNamer._get_kw_model')
def test_normal_pipeline_does_not_call_keybert_and_uses_simple_names(mock_get_kw_model):
    """Test 1 & 2: Normal pipeline doesn't call KeyBERT and generates simple names."""
    from app.clustering.cluster_namer import ClusterNamer
    
    # Run the cluster namer like the incident pipeline does
    namer = ClusterNamer()
    cluster_summaries = [MagicMock(cluster_id=1)]
    combined_texts = ["password reset", "reset my password"]
    cluster_labels = [1, 1]
    
    summaries = namer.name_clusters(cluster_summaries, combined_texts, cluster_labels)
    
    assert summaries[0].cluster_name == "Password Reset Issues"
    mock_get_kw_model.assert_not_called()

# =======================================================================
# Test 3 & 4: AI Enrichment Success
# =======================================================================

@patch('app.clustering.cluster_namer.AIClusterNamer._get_kw_model')
def test_ai_enrichment_invokes_keybert_and_updates_names(mock_get_kw_model):
    """Test 3 & 4: Enrichment invokes KeyBERT and updates cluster names."""
    cluster_id = seed_cluster_data()
    
    mock_kw_model = MagicMock()
    mock_kw_model.extract_keywords.return_value = [("AI Enriched Name", 0.9)]
    mock_get_kw_model.return_value = mock_kw_model
    
    job_service = JobService(scheduler_service=MagicMock())
    job = job_service.create_enrichment_job()
    
    enrichment_service = EnrichmentService()
    enrichment_service.process_enrichment_job(str(job.id))
    
    mock_kw_model.extract_keywords.assert_called()
    
    session = SessionLocal()
    cluster = session.query(Cluster).filter_by(cluster_id=cluster_id).first()
    assert cluster.naming_status == "AI_ENRICHED"
    assert cluster.ai_cluster_name == "Ai Enriched Name Issues"
    assert cluster.cluster_name == "Ai Enriched Name Issues"
    
    job = session.query(ProcessingJob).filter_by(id=job.id).first()
    assert job.status == JOB_STATUS_COMPLETED
    session.close()

# =======================================================================
# Test 5: 3R Invariant
# =======================================================================

@patch('app.clustering.cluster_namer.AIClusterNamer._get_kw_model')
def test_3r_results_remain_identical(mock_get_kw_model):
    """Test 5: 3R results remain identical before and after enrichment."""
    cluster_id = seed_cluster_data()
    
    mock_kw_model = MagicMock()
    mock_kw_model.extract_keywords.return_value = [("AI Enriched Name", 0.9)]
    mock_get_kw_model.return_value = mock_kw_model
    
    # Pre-enrichment state
    session = SessionLocal()
    pre_cluster = session.query(Cluster).filter_by(cluster_id=cluster_id).first()
    pre_incident = session.query(Incident).filter_by(cluster_id=cluster_id).first()
    assert pre_cluster.three_r_category == "RUNNER"
    assert pre_incident.three_r_category == "RUNNER"
    session.close()
    
    job_service = JobService(scheduler_service=MagicMock())
    job = job_service.create_enrichment_job()
    
    enrichment_service = EnrichmentService()
    enrichment_service.process_enrichment_job(str(job.id))
    
    # Post-enrichment state
    session = SessionLocal()
    post_cluster = session.query(Cluster).filter_by(cluster_id=cluster_id).first()
    post_incident = session.query(Incident).filter_by(cluster_id=cluster_id).first()
    
    # Name changed
    assert post_cluster.cluster_name == "Ai Enriched Name Issues"
    
    # But 3R categorization and counts did not
    assert post_cluster.three_r_category == "RUNNER"
    assert post_cluster.incident_count == 5
    assert post_incident.three_r_category == "RUNNER"
    session.close()

# =======================================================================
# Test 6: Reject when no dataset
# =======================================================================

def test_no_processed_dataset_enrichment_rejected():
    """Test 6: No processed dataset -> enrichment rejected."""
    # Ensure DB is empty
    clear_db()
    
    job_service = JobService(scheduler_service=MagicMock())
    
    with pytest.raises(ValueError, match="No processed dataset is available"):
        job_service.create_enrichment_job()

# =======================================================================
# Test 7: Reject when core processing running
# =======================================================================

def test_core_processing_running_enrichment_rejected():
    """Test 7: Core processing running -> enrichment rejected."""
    seed_cluster_data()
    
    session = SessionLocal()
    job = ProcessingJob(
        dataset_path="",
        job_type="PROCESSING",
        status=JOB_STATUS_RUNNING
    )
    session.add(job)
    session.commit()
    session.close()
    
    job_service = JobService(scheduler_service=MagicMock())
    with pytest.raises(ValueError, match="after dataset processing is complete"):
        job_service.create_enrichment_job()

# =======================================================================
# Test 8: Reject duplicate enrichment
# =======================================================================

def test_duplicate_enrichment_rejected():
    """Test 8: Duplicate enrichment -> second request rejected."""
    seed_cluster_data()
    
    session = SessionLocal()
    job = ProcessingJob(
        dataset_path="",
        job_type=JOB_TYPE_AI_CLUSTER_NAMING,
        status=JOB_STATUS_RUNNING
    )
    session.add(job)
    session.commit()
    session.close()
    
    job_service = JobService(scheduler_service=MagicMock())
    with pytest.raises(ValueError, match="already running"):
        job_service.create_enrichment_job()

# =======================================================================
# Test 9 & 10: KeyBERT Failure Safety
# =======================================================================

@patch('app.clustering.cluster_namer.AIClusterNamer._get_kw_model')
def test_keybert_failure_keeps_simple_names(mock_get_kw_model):
    """Test 9 & 10: KeyBERT unavailable or fails -> clear failure, simple names intact."""
    cluster_id = seed_cluster_data()
    
    mock_get_kw_model.side_effect = RuntimeError("Failed to load KeyBERT")
    
    job_service = JobService(scheduler_service=MagicMock())
    job = job_service.create_enrichment_job()
    
    enrichment_service = EnrichmentService()
    
    # Enrichment should fail gracefully
    enrichment_service.process_enrichment_job(str(job.id))
    
    session = SessionLocal()
    cluster = session.query(Cluster).filter_by(cluster_id=cluster_id).first()
    
    # Names should remain intact
    assert cluster.naming_status == "STANDARD"
    assert cluster.cluster_name == "Term Frequency Name"
    
    job = session.query(ProcessingJob).filter_by(id=job.id).first()
    assert job.status == JOB_STATUS_FAILED
    assert "Failed to load KeyBERT" in job.error_message
    session.close()
