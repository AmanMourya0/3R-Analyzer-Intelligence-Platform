"""
Upload schemas.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """
    Upload response.
    """

    filename: str
    dataset_path: str
    size: int