"""
Processing job ORM model.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from app.constants import JOB_STATUS_PENDING
from app.database.base import Base


class ProcessingJob(Base):
    """
    PostgreSQL record that tracks asynchronous processing work.
    """

    __tablename__ = "processing_jobs"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    dataset_path = Column(
        String(1000),
        nullable=False
    )

    source_type = Column(String(30), nullable=False, default="upload")

    job_type = Column(
        String(30),
        nullable=False,
        default="PROCESSING"
    )
    assignment_groups = Column(Text, nullable=True)

    start_date = Column(DateTime, nullable=True)

    end_date = Column(DateTime, nullable=True)

    status = Column(
        String(30),
        nullable=False,
        default=JOB_STATUS_PENDING
    )

    message = Column(
        String(500),
        nullable=False,
        default="Processing job queued."
    )

    progress_stage = Column(
        String(100),
        nullable=False,
        default="QUEUED"
    )

    progress_message = Column(
        String(500),
        nullable=False,
        default="Processing job queued."
    )

    progress_percent = Column(
        Integer,
        nullable=False,
        default=0
    )

    processing_time_seconds = Column(
        Float,
        nullable=True
    )

    total_incidents = Column(
        Integer,
        nullable=True
    )

    total_clusters = Column(
        Integer,
        nullable=True
    )

    total_problem_candidates = Column(
        Integer,
        nullable=True
    )

    total_runners = Column(Integer, nullable=True)

    total_repeaters = Column(Integer, nullable=True)

    total_rares = Column(Integer, nullable=True)

    error_message = Column(
        Text,
        nullable=True
    )


    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
