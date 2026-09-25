"""
Processing jobs API.
"""

from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from app.core.dependencies import get_job_service
from app.schemas import JobResponse
from app.services.job_service import JobService
from app.utils.logger import logger

router = APIRouter(
    prefix="/jobs",
    tags=["Processing Jobs"]
)


@router.get(
    "",
    response_model=List[JobResponse],
    status_code=status.HTTP_200_OK,
    summary="List Processing Jobs"
)
def list_jobs(
    service: JobService = Depends(get_job_service)
) -> List[JobResponse]:
    """
    Return all processing jobs.
    """

    try:

        return service.list_jobs()

    except Exception as ex:

        logger.exception(
            "Failed to list processing jobs."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Processing Job"
)
def get_job(
    job_id: str,
    service: JobService = Depends(get_job_service)
) -> JobResponse:
    """
    Return one processing job by UUID.
    """

    try:

        job = service.get_job(
            job_id
        )

        if job is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processing job not found."
            )

        return job

    except HTTPException:

        raise

    except Exception as ex:

        logger.exception(
            "Failed to fetch processing job %s.",
            job_id
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(ex)
        )
