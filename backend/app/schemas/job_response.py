"""
Processing job response schema.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class JobResponse(BaseModel):
    """
    Response model for asynchronous processing jobs.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID

    dataset_path: str

    source_type: str = "upload"

    status: str

    message: str

    progress_stage: str

    progress_message: str

    progress_percent: int
    
    processing_time_seconds: Optional[float] = Field(
        default=None,
        ge=0
    )

    total_incidents: Optional[int] = Field(
        default=None,
        ge=0
    )

    total_clusters: Optional[int] = Field(
        default=None,
        ge=0
    )

    total_problem_candidates: Optional[int] = Field(
        default=None,
        ge=0
    )

    total_runners: Optional[int] = Field(default=None, ge=0)
    total_repeaters: Optional[int] = Field(default=None, ge=0)
    total_rares: Optional[int] = Field(default=None, ge=0)

    error_message: Optional[str] = None

    created_at: datetime

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    updated_at: datetime


class PaginatedJobResponse(BaseModel):
    """
    Paginated response model for asynchronous processing jobs.
    """
    jobs: list[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
