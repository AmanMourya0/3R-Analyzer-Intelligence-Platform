"""
Dataset Upload API.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status

from app.schemas import UploadResponse
from app.utils.logger import logger

router = APIRouter(
    prefix="/upload",
    tags=["Dataset Upload"]
)

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    ".xlsx",
    ".xls",
    ".csv",
}


@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Dataset"
)
async def upload_dataset(
    file: UploadFile = File(...)
) -> UploadResponse:

    suffix = Path(file.filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="Only Excel and CSV files are supported."

        )

    unique_name = (
        f"{uuid4().hex}{suffix}"
    )

    destination = (
        UPLOAD_DIRECTORY / unique_name
    )

    with destination.open(
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    logger.info(
        "Dataset uploaded: %s",
        destination
    )

    return UploadResponse(

        filename=file.filename,

        dataset_path=str(destination),

        size=destination.stat().st_size

    )