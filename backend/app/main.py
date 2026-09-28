"""
Application Entry Point

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings

from app.api.jobs import router as jobs_router
from app.api.process import router as process_router

from app.core.dependencies import (
    get_scheduler_service,
)

from app.database.init_db import initialize_database
from app.database.database import SessionLocal

from app.utils.logger import logger
from app.api.dashboard import router as dashboard_router
from app.api.upload import router as upload_router
from app.api.analytics import router as analytics_router
from app.api.reports import router as reports_router
from app.api.frontend_api import router as frontend_api_router
from sqlalchemy import text
from fastapi import Response


# ==========================================================
# Application Lifecycle
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    """

    logger.info("=" * 80)
    logger.info("Starting 3R Analyzer Intelligence...")

    # -----------------------------------------------------------------
    # NOTE:
    # initialize_database() is kept only for local development.
    # Replace this with Alembic migrations before production deployment.
    # -----------------------------------------------------------------
    initialize_database()

    scheduler = get_scheduler_service()

    scheduler.start()

    logger.info("Application startup completed successfully.")

    yield

    logger.info("Stopping application...")

    scheduler.shutdown()

    logger.info("Application shutdown completed.")


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title=settings.APP_NAME,
    version="0.3.0",
    description="Recurring Incident Intelligence Platform",
    lifespan=lifespan
)

# ============================================================================
# Cross-Origin Resource Sharing (CORS)
# Allows the React frontend to communicate with the FastAPI backend.
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# API Routers
# ==========================================================


app.include_router(process_router)

app.include_router(jobs_router)

app.include_router(dashboard_router)

app.include_router(upload_router)
app.include_router(analytics_router)
app.include_router(reports_router)

# Frontend Compatibility API
app.include_router(frontend_api_router)


# ==========================================================
# Root Endpoint
# ==========================================================

@app.get("/", tags=["Application"])
def root() -> dict:
    """
    Health check endpoint.
    """

    return {
        "status": "Running",
        "application": "3R Analyzer Intelligence",
        "version": "0.3.0"
    }

@app.get("/health", tags=["Application"])
def health_check() -> dict:
    '''Process liveness check.'''
    return {"status": "ok", "service": settings.APP_NAME}

@app.get("/ready", tags=["Application"])
def readiness_check(response: Response) -> dict:
    '''Dependencies check (e.g., PostgreSQL).'''
    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        session.close()
        return {"status": "ready"}
    except Exception as e:
        logger.exception("Readiness check failed")
        response.status_code = 503
        return {"status": "error", "detail": "Database unavailable"}
