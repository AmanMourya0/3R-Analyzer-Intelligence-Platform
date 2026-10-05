import pytest
from unittest.mock import MagicMock, patch
import numpy as np

from app.clustering.embedding import SemanticEmbeddingGenerator
from app.core.exceptions import JobCancelledException
from app.config.settings import settings


def test_cooperative_cancellation_during_embedding():
    """
    Simulates embedding generation with batches, where cancellation
    is requested during the process, ensuring it stops safely.
    """
    settings.EMBEDDING_BATCH_SIZE = 2
    texts = ["incident 1", "incident 2", "incident 3", "incident 4", "incident 5"]
    
    # Mock the SentenceTransformer to track how many times it was called
    mock_model = MagicMock()
    # It returns dummy embeddings of shape (batch_size, 384)
    mock_model.encode.side_effect = lambda batch, **kwargs: np.zeros((len(batch), 384))
    
    with patch("app.clustering.embedding.SentenceTransformer", return_value=mock_model):
        generator = SemanticEmbeddingGenerator()
        
        # We will trigger cancellation after the second batch
        state = {"batches_processed": 0}
        
        def mock_cancelled_check():
            if state["batches_processed"] >= 2:
                raise JobCancelledException("Job was cancelled by the user.")
            state["batches_processed"] += 1
            
        with pytest.raises(JobCancelledException):
            generator.generate_embeddings(texts, check_cancellation=mock_cancelled_check)
            
        # Total texts = 5, Batch size = 2
        # Batch 1: check (0 < 2 -> ok), processed = 1
        # encode called (1)
        # Batch 2: check (1 < 2 -> ok), processed = 2
        # encode called (2)
        # Batch 3: check (2 >= 2 -> raise!)
        # encode never called for batch 3
        
        assert mock_model.encode.call_count == 2

def test_cancellation_telemetry_and_status():
    from app.services.performance.stage_timer import stage_timer, PipelineProfiler
    from unittest.mock import patch
    
    profiler = PipelineProfiler.get_instance()
    profiler.current_job_id = "test-job-id"
    
    # 1. Test telemetry
    with patch("app.utils.logger.logger") as mock_logger:
        with pytest.raises(JobCancelledException):
            with stage_timer("GENERATING_EMBEDDINGS"):
                raise JobCancelledException("User cancel", reason="USER_REQUESTED")
                
        found_cancelled = False
        for call in mock_logger.info.mock_calls:
            msg = call.args[0]
            if "stage=GENERATING_EMBEDDINGS" in msg and "status=CANCELLED" in msg:
                found_cancelled = True
                break
                
        assert found_cancelled, "Should have logged status=CANCELLED for the stage telemetry"
        
    # 2. Test ProcessService status handling
    from app.services.process_service import ProcessService
    from app.database.database import SessionLocal, engine
    from app.database.base import Base
    from app.database.processing_job_model import ProcessingJob
    from app.constants import JOB_STATUS_PENDING, JOB_STATUS_RUNNING, JOB_STATUS_CANCELLED, JOB_STATUS_FAILED
    
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    session.query(ProcessingJob).delete()
    session.commit()
    
    job = ProcessingJob(
        dataset_path="dummy.csv",
        source_type="upload",
        status=JOB_STATUS_PENDING,
        progress_stage="QUEUED",
        progress_percent=0
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    
    def mock_pipeline_run(*args, **kwargs):
        from app.services.job_service import JobService
        from app.repositories.job_repository import JobRepository
        db = SessionLocal()
        JobService(JobRepository(db)).cancel_job(str(job.id))
        db.close()
        raise JobCancelledException("Cancelled", reason="USER_REQUESTED")

    pipeline_mock = MagicMock()
    pipeline_mock.run.side_effect = mock_pipeline_run
    
    service = ProcessService(pipeline=pipeline_mock)
    
    with patch("app.services.process_service.IncidentLoader"):
        with patch("app.services.process_service.ProcessService._apply_processing_scope"):
            service.process_job(str(job.id))
            
    session.refresh(job)
    
    # Ensure it's not marked FAILED by the exception handler
    assert job.status != JOB_STATUS_FAILED
    # Ensure it remains CANCELLED
    assert job.status == JOB_STATUS_CANCELLED
    
    session.close()

def test_cancellation_pipeline_logging():
    from app.pipelines.incident_pipeline import IncidentPipeline
    from unittest.mock import patch
    import pandas as pd
    
    pipeline = IncidentPipeline()
    df = pd.DataFrame({"Incident Number": ["INC001"]})
    
    def failing_cancellation_check():
        raise JobCancelledException("User cancel", reason="USER_REQUESTED")
        
    with patch("app.pipelines.incident_pipeline.logger") as mock_logger:
        with pytest.raises(JobCancelledException):
            pipeline.run(df, check_cancellation=failing_cancellation_check)
            
        found_info = False
        found_error = False
        
        for call in mock_logger.info.mock_calls:
            msg = call.args[0]
            if "cancelled" in str(msg).lower():
                found_info = True
                
        for call in mock_logger.exception.mock_calls + mock_logger.error.mock_calls:
            msg = call.args[0]
            if "failed" in str(msg).lower() or "error" in str(msg).lower():
                found_error = True
                
        assert found_info, "Pipeline should log cancellation at INFO level"
        assert not found_error, "Pipeline should NOT log cancellation as an error or failure"
