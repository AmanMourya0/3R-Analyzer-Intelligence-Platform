"""
Frontend Compatibility API Router

Exposes /api/* endpoints that exactly match what the Friend frontend
(01_FRIEND_3R_ANALYZER/frontend) expects.

All business logic is delegated to FrontendCompatibilityService,
which in turn uses the production repositories and DB models.

DO NOT add production business logic directly to route handlers here.

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status, Response, Path as FastAPIPath

from app.core.dependencies import get_job_service
from app.services.job_service import JobService
from app.services.frontend_compatibility_service import FrontendCompatibilityService
from app.services.report_service import report_service
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["Frontend Compatibility API"])

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

# Sample dataset shipped with the production backend
SAMPLE_DATASET_PATH = "dataset/Dummy_Incident_Dataset_V2_5000.xlsx"

# Singleton compatibility service (stateless, thread-safe)
_compat_service = FrontendCompatibilityService()


# ==============================================================
# HEALTH
# ==============================================================

@router.get("/health", summary="Frontend health check")
def api_health():
    """
    Health check endpoint.
    App.jsx calls GET /api/health on startup and reads:
      { status, data_loaded }
    """
    return _compat_service.get_health()


# ==============================================================
# WARMUP
# ==============================================================

@router.get("/warmup", summary="Model warmup (no-op)")
def api_warmup():
    """
    The frontend calls GET /api/warmup after health passes.
    Production models load at startup via dependency injection.
    This endpoint is a compatibility no-op.
    """
    return {"status": "ready", "message": "Models loaded at startup."}


# ==============================================================
# UPLOAD — single-step upload + process
# ==============================================================

@router.post("/upload", summary="Upload CSV/XLSX and start processing")
async def api_upload(
    file: UploadFile = File(...),
    job_service: JobService = Depends(get_job_service),
):
    """
    Single-step upload compatible with Friend frontend:
      1. Validate file type
      2. Save to uploads/ using production path convention
      3. Create a production ProcessingJob via JobService
      4. JobService -> SchedulerService -> APScheduler -> ProcessService
      5. Return immediately (frontend will poll /api/status)
    """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV and Excel files are supported.",
        )

    unique_name = f"{uuid4().hex}{suffix}"
    destination = UPLOAD_DIRECTORY / unique_name

    with destination.open("wb") as buf:
        shutil.copyfileobj(file.file, buf)

    logger.info("Frontend upload saved: %s", destination)

    try:
        job = job_service.create_processing_job(
            dataset_path=str(destination),
            source_type="upload",
        )
        logger.info("Created processing job %s for frontend upload.", job.id)
    except Exception as exc:
        logger.exception("Failed to create processing job for frontend upload.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File saved but processing could not start: {exc}",
        )

    return {"status": "queued", "message": "File uploaded and processing started.", "job_id": str(job.id)}


# ==============================================================
# LOAD SAMPLE
# ==============================================================

@router.post("/load-sample", summary="Load bundled sample dataset and process")
def api_load_sample(
    job_service: JobService = Depends(get_job_service),
):
    """
    Load the bundled production sample dataset and start processing.
    Equivalent to clicking Load Sample in the sidebar.
    """
    sample_path = Path(SAMPLE_DATASET_PATH)
    if not sample_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample dataset not found at {SAMPLE_DATASET_PATH}",
        )

    try:
        job = job_service.create_processing_job(
            dataset_path=str(sample_path),
            source_type="upload",
        )
        logger.info("Sample dataset job created: %s", job.id)
    except Exception as exc:
        logger.exception("Failed to create processing job for sample dataset.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not start sample processing: {exc}",
        )

    return {"status": "queued", "message": "Sample data processing started.", "job_id": str(job.id)}


# ==============================================================
# STATUS — job progress polling
# ==============================================================

@router.get("/status", summary="Latest job processing status")
def api_status():
    """
    Returns latest job status in Friend frontend format:
    { status: "idle"|"processing"|"done"|"error", message, result }
    App.jsx pollStatus() reads status=="done" to navigate to dashboard.
    """
    return _compat_service.get_status()


# ==============================================================
# DASHBOARD
# ==============================================================

@router.get("/dashboard", summary="Frontend dashboard analytics")
def api_dashboard():
    """
    Returns dashboard data in Dashboard.jsx format:
    { total_tickets, total_clusters, recurring_issue_percentage,
      noise_ticket_count, top_clusters }
    """
    return _compat_service.get_dashboard()


# ==============================================================
# CLUSTERS
# ==============================================================

@router.get("/clusters", summary="All clusters for Clusters page")
def api_clusters():
    """
    Returns { clusters: [{cluster_id, cluster_name, ticket_count, ci_names, ...}] }
    """
    return _compat_service.get_clusters()


@router.get("/clusters/{cluster_id}", summary="Single cluster detail")
def api_cluster_detail(cluster_id: int):
    """
    Returns full intelligence detail for a single cluster.
    """
    result = _compat_service.get_cluster_detail(cluster_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Cluster {cluster_id} not found.")
    return result


# ==============================================================
# TICKETS
# ==============================================================

@router.get("/tickets", summary="Filtered ticket list")
def api_tickets(
    cluster_id: Optional[int] = Query(None),
    ci_name: Optional[str] = Query(None),
    assigned_group: Optional[str] = Query(None),
    three_r_category: Optional[str] = Query(None),
    filter: Optional[str] = Query(None, description="JSON encoded FilterGroup AST"),
    sort: Optional[str] = Query(None, description="JSON encoded SortRule list"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    limit: int = Query(1000, le=5000),  # kept for legacy
):
    """
    Returns { tickets: [...], total: int, page: int, page_size: int, total_pages: int }
    Supports legacy filters + AST structured filters.
    """
    return _compat_service.get_tickets(
        cluster_id=cluster_id,
        ci_name=ci_name,
        assigned_group=assigned_group,
        three_r_category=three_r_category,
        filter_json=filter,
        sort_json=sort,
        page=page,
        page_size=page_size,
        limit=limit,
    )


# ==============================================================
# EXPORT & REPORTING
# ==============================================================

@router.get("/export/tickets/csv", summary="Export tickets to CSV")
def export_tickets_csv(
    filter: Optional[str] = Query(None, description="JSON encoded FilterGroup AST"),
    sort: Optional[str] = Query(None, description="JSON encoded SortRule list")
):
    """Exports tickets exactly matching current filters to a CSV attachment."""
    content = report_service.export_tickets_csv(filter_json=filter, sort_json=sort)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=3R_Tickets_Export.csv"}
    )

@router.get("/export/clusters/csv", summary="Export clusters to CSV")
def export_clusters_csv():
    """Exports cluster analytics to a CSV attachment."""
    content = report_service.export_clusters_csv()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=3R_Cluster_Report.csv"}
    )

@router.get("/export/summary/csv", summary="Export 3R Summary to CSV")
def export_summary_csv():
    """Exports 3R summary analytics to a CSV attachment."""
    content = report_service.export_3r_summary_csv()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=3R_Summary_Report.csv"}
    )

@router.get("/export/executive-report/pdf", summary="Generate Executive Report PDF")
def export_executive_report_pdf(
    filter: Optional[str] = Query(None, description="JSON encoded FilterGroup AST"),
    sort: Optional[str] = Query(None, description="JSON encoded SortRule list")
):
    """Generates a leadership-ready PDF report covering the given scope."""
    content = report_service.generate_executive_report_pdf(filter_json=filter, sort_json=sort)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=3R_Executive_Report.pdf"}
    )


# ==============================================================
# CI ANALYSIS
# ==============================================================

@router.get("/ci-list", summary="Configuration item list")
def api_ci_list():
    """
    Returns { ci_list: [{ci_name, total_tickets, recurring_tickets,
      recurring_percentage, cluster_count}] }
    """
    return _compat_service.get_ci_list()


@router.get("/ci-clusters", summary="Cluster detail for a CI")
def api_ci_clusters(ci_name: str = Query(...)):
    """
    Returns drill-down data for CIAnalysis detail view:
    { ci_name, total_tickets, recurring_tickets, recurring_percentage, clusters }
    """
    return _compat_service.get_ci_clusters(ci_name)


# ==============================================================
# ASSIGNMENT GROUP ANALYSIS
# ==============================================================

@router.get("/group-list", summary="Assignment group list")
def api_group_list():
    """
    Returns { group_list: [{group_name, total_tickets, recurring_tickets,
      recurring_percentage, cluster_count}] }
    """
    return _compat_service.get_group_list()


@router.get("/group-clusters", summary="Cluster detail for an assignment group")
def api_group_clusters(group_name: str = Query(...)):
    """
    Returns drill-down data for AssignedGroup detail view:
    { group_name, total_tickets, recurring_tickets, recurring_percentage, clusters }
    """
    return _compat_service.get_group_clusters(group_name)


# ==============================================================
# SERVICENOW — deferred, returns informative response
# ==============================================================

@router.get("/servicenow-groups", summary="ServiceNow groups (deferred)")
def api_servicenow_groups():
    """
    ServiceNow integration is deferred. Returns empty list.
    The Home.jsx SNFilters component reads from /public/sample_tickets.csv
    directly, so this endpoint is not critical for core functionality.
    """
    return {"groups": []}


@router.post("/servicenow-import", summary="ServiceNow import (deferred)")
def api_servicenow_import():
    """
    ServiceNow import deferred. Returns informative message.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="ServiceNow import is not yet available. Please use CSV upload.",
    )


# ==============================================================
# CLEAR — gracefully unsupported in production
# ==============================================================

@router.delete("/clear", summary="Clear data (not supported in production)")
def api_clear():
    """
    The production backend uses PostgreSQL — data is persistent.
    Clearing all data via API is not supported for safety.
    """
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Data clearing is not supported in production. Use the database directly.",
    )

# ==============================================================
# PREDICT (Phase 10 - deferred)
# ==============================================================

@router.post("/predict", summary="Ticket prediction (deferred)")
def api_predict():
    """
    Prediction endpoint (Demo page). Deferred to Phase 10.
    Returns 501 so the Demo page can handle gracefully.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Ticket prediction is not yet available. Upload a dataset to analyze clusters.",
    )

# ==============================================================
# JOBS
# ==============================================================

@router.get("/jobs", summary="Paginated historical jobs")
def api_jobs_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    job_service: JobService = Depends(get_job_service)
):
    """
    Paginated processing jobs history.
    """
    try:
        jobs, total, total_pages = job_service.list_jobs_paginated(
            page=page,
            page_size=page_size,
            status=status_filter
        )
        return {
            "jobs": jobs,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.exception("Failed to fetch jobs.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/jobs/{job_id}", summary="Get job details")
def api_job_detail(
    job_id: str = FastAPIPath(...),
    job_service: JobService = Depends(get_job_service)
):
    """
    Get detailed information about a specific processing job.
    """
    try:
        job = job_service.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Processing job not found."
            )
        return job
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to fetch job %s", job_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
