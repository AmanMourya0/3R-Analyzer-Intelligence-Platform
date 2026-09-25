"""
Processing Request Schema

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from typing import Literal
from datetime import date


class ProcessRequest(BaseModel):
    """
    Request schema for dataset processing.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    dataset_path: str = Field(
        ...,
        description="Path of uploaded dataset.",
        examples=["dataset/Dummy_Incident_Dataset_V2_5000.xlsx"]
    )

    source_type: Literal["upload", "servicenow"] = "upload"

    assignment_groups: list[str] | None = Field(default=None)

    start_date: date | None = None

    end_date: date | None = None
