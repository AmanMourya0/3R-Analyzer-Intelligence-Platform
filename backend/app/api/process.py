"""
Incident Processing API

Handles dataset processing requests.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from app.core.dependencies import get_job_service
from app.schemas import (
    JobResponse,
    ProcessRequest,
)
from app.services.job_service import JobService
from app.utils.logger import logger

router = APIRouter(
    prefix="/process",
    tags=["Incident Processing"]
)


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Process Incident Dataset",
    description="Queues the incident dataset for asynchronous processing."
)
def process_dataset(
    request: ProcessRequest,
    service: JobService = Depends(get_job_service)
) -> JobResponse:
    """
    Queue the incident dataset for asynchronous processing.

    Parameters
    ----------
    request : ProcessRequest
        Dataset processing request.

    service : JobService
        Injected job service.

    Returns
    -------
    JobResponse
        Queued processing job.
    """

    logger.info("=" * 80)
    logger.info("Received dataset processing request.")
    logger.info("Dataset Path : %s", request.dataset_path)

    try:

        job = service.create_processing_job(
            request.dataset_path,
            source_type=request.source_type,
            assignment_groups=request.assignment_groups,
            start_date=request.start_date,
            end_date=request.end_date,
        )

        logger.info(
            "Dataset processing job %s accepted.",
            job.id
        )

        return job

    except Exception as ex:

        logger.exception(
            "Dataset processing failed."
        )

        raise HTTPException(

            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,

            detail=str(ex)

        )


@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    include_in_schema=False
)
def process_dataset_with_trailing_slash(
    request: ProcessRequest,
    service: JobService = Depends(get_job_service)
) -> JobResponse:
    """
    Backward-compatible trailing-slash process endpoint.
    """

    return process_dataset(
        request=request,
        service=service
    )
