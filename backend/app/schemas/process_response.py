"""
Processing Response Schema

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ProcessResponse(BaseModel):
    """
    Response returned after processing.
    """

    model_config = ConfigDict(
        from_attributes=True
    )

    status: str

    message: str

    processing_time_seconds: float = Field(
        ...,
        ge=0
    )

    total_incidents: int = Field(
        ...,
        ge=0
    )

    total_clusters: int = Field(
        ...,
        ge=0
    )

    total_problem_candidates: int = Field(
        ...,
        ge=0
    )