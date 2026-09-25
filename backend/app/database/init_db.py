"""
Database Initialization
"""

from app.database.database import engine
from app.database.base import Base

# Import all models so SQLAlchemy registers them
from app.database.incident_model import Incident
from app.database.cluster_model import Cluster
from app.database.recurrence_model import Recurrence
from app.database.processing_job_model import ProcessingJob

def initialize_database() -> None:
    """
    Create all database tables.
    """
    Base.metadata.create_all(bind=engine)
