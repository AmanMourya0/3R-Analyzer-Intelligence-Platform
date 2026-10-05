"""
Tests for Clear Data and Sample Data endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from app.main import app
from app.api.frontend_api import get_session
from app.database.processing_job_model import ProcessingJob
from app.database.incident_model import Incident
from app.database.cluster_model import Cluster
from app.database.recurrence_model import Recurrence
from app.constants import JOB_STATUS_PENDING, JOB_STATUS_RUNNING, JOB_STATUS_COMPLETED

client = TestClient(app)

def test_clear_data_success():
    """Test successful clear data transaction."""
    mock_session = MagicMock(spec=Session)
    
    # Mock active jobs count to 0
    mock_query = MagicMock()
    mock_query.filter.return_value.count.return_value = 0
    
    def query_side_effect(model):
        if model == ProcessingJob:
            return mock_query
        return MagicMock()
    
    mock_session.query.side_effect = query_side_effect

    app.dependency_overrides[get_session] = lambda: mock_session

    response = client.delete("/api/clear")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    
    # Verify commit was called
    assert mock_session.commit.called
    
    app.dependency_overrides.clear()


def test_clear_data_fails_when_processing():
    """Test clear data aborts if jobs are running."""
    mock_session = MagicMock(spec=Session)
    
    # Mock active jobs count to 1
    mock_query = MagicMock()
    mock_query.filter.return_value.count.return_value = 1
    
    def query_side_effect(model):
        if model == ProcessingJob:
            return mock_query
        return MagicMock()
    
    mock_session.query.side_effect = query_side_effect

    app.dependency_overrides[get_session] = lambda: mock_session

    response = client.delete("/api/clear")
    assert response.status_code == 400
    assert "Cannot clear data while processing is active" in response.json()["detail"]
    
    app.dependency_overrides.clear()


@patch("app.api.frontend_api.Path")
def test_download_sample_success(mock_path_class):
    """Test downloading the canonical sample dataset."""
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    mock_path.name = "Dummy_Incident_Dataset_V2_5000.xlsx"
    mock_path.__str__.return_value = "dataset/Dummy_Incident_Dataset_V2_5000.xlsx"
    
    mock_path_class.return_value = mock_path
    
    # Use patch for FileResponse because returning an actual file in tests might need a real file
    with patch("fastapi.responses.FileResponse") as mock_file_response:
        mock_file_response.return_value = {"mock": "response"}
        
        # Test directly with FastAPI routing by simulating
        from app.api.frontend_api import api_download_sample
        result = api_download_sample()
        
        assert mock_file_response.called
        kwargs = mock_file_response.call_args[1]
        assert kwargs["path"] == "dataset/Dummy_Incident_Dataset_V2_5000.xlsx"
        assert kwargs["filename"] == "Dummy_Incident_Dataset_V2_5000.xlsx"
